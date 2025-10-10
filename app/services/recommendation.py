# services/ranking_engine.py

from typing import Dict, List, Tuple
from app.schemas.ranking import UserData, Priority, FeaturePriority

CarSpec = Dict[str, object]

# Demo catalog: add a simple reliability proxy (1–5). In production, source this from service history/claims/TCO.
CATALOG: List[CarSpec] = [
    {
        "mmv": "Maruti Swift ZXI AMT",
        "bodyType": "Hatchbacks",
        "fuelType": "Petrol",
        "price": 1000000,
        "mileage_kmpl": 22.0,
        "safety_airbags": 2,
        "has_esp": False,
        "features": {"rear_camera": True, "cruise_control": False, "wireless_android_auto": True},
        "performance_power_hp": 90,
        "brand_value": 2,
        "boot_liters": 268,
        "music_quality": 2,
        "reliability_score": 4,  # 1–5 (higher is better)
    },
    {
        "mmv": "Tata Punch Creative AMT",
        "bodyType": "SUV",
        "fuelType": "Petrol",
        "price": 1100000,
        "mileage_kmpl": 20.5,
        "safety_airbags": 2,
        "has_esp": True,
        "features": {"rear_camera": True, "cruise_control": True, "wireless_android_auto": True},
        "performance_power_hp": 88,
        "brand_value": 3,
        "boot_liters": 366,
        "music_quality": 2,
        "reliability_score": 4,
    },
    {
        "mmv": "Hyundai i20 Asta (O) DCT",
        "bodyType": "Hatchbacks",
        "fuelType": "Petrol",
        "price": 1400000,
        "mileage_kmpl": 19.5,
        "safety_airbags": 6,
        "has_esp": True,
        "features": {"rear_camera": True, "cruise_control": True, "wireless_android_auto": True},
        "performance_power_hp": 118,
        "brand_value": 3,
        "boot_liters": 311,
        "music_quality": 3,
        "reliability_score": 3,
    },
]


def build_feature_tags(car: CarSpec) -> List[str]:
    tags: List[str] = []
    airbags = int(car.get("safety_airbags", 0))
    esp = bool(car.get("has_esp"))
    feats = car.get("features", {})

    if airbags >= 6:
        tags.append("6 airbags")
    elif airbags >= 4:
        tags.append(f"{airbags} airbags")
    elif airbags > 0:
        tags.append(f"{airbags} airbags")

    if esp:
        tags.append("ESP")

    if feats.get("rear_camera"):
        tags.append("rear camera")
    if feats.get("cruise_control"):
        tags.append("cruise control")
    if feats.get("wireless_android_auto"):
        tags.append("wireless Android Auto")

    return tags


def build_reason(s: dict, weights: Dict[Priority, float], car: CarSpec, user: UserData) -> str:
    # Core contributions including reliability preceding features
    contributions = [
        ("safety",       weights[Priority.safety]       * s["safety"]),
        ("reliability",  s["reliability"]),  # treated as first-class dimension
        ("mileage",      weights[Priority.mileage]      * s["mileage"]),
        ("cheap to run", weights[Priority.cheap_to_run] * s["cheap_to_run"]),
        ("performance",  weights[Priority.performance]  * s["performance"]),
        ("features",     weights[Priority.features]     * s["features"]),
    ]
    contributions.sort(key=lambda x: x[1], reverse=True)
    top_core = [name for name, _ in contributions[:2]]

    feature_tags = build_feature_tags(car)
    # Prefer showing safety-related tags first
    safety_first = [t for t in feature_tags if ("airbags" in t or t == "ESP")]
    others = [t for t in feature_tags if t not in safety_first]
    ordered = safety_first + others
    tags_text = f" ({', '.join(ordered[:3])})" if ordered else ""

    bonus_bits = []
    # Luxury/convenience bonuses acknowledged but secondary
    if s["feature_bonus"] >= 0.2:
        bonus_bits.append("robust safety equipment")
    elif s["feature_bonus"] >= 0.1:
        bonus_bits.append("useful convenience features")

    if s["music_alignment"] >= 0.6 and user.other_preferences.music_importance >= 7:
        bonus_bits.append("good audio for your music preference")

    penalty_bits = []
    if s["brand_alignment"] >= 0.6:
        penalty_bits.append("brand may not match preference")

    parts = []
    if top_core:
        parts.append(f"Prioritizes {', '.join(top_core)}{tags_text}")
    if bonus_bits:
        parts.append(f"plus {' and '.join(bonus_bits)}")
    if penalty_bits:
        parts.append(f"but {', '.join(penalty_bits)}")

    return (" ".join(parts) + ".") if parts else "Safe and reliable pick within budget."


def rank_cars(user: UserData, top_n: int = 5) -> List[Dict[str, object]]:
    """
    Rank cars with explicit priority: safety and reliability first, then efficiency and cost,
    and luxury/convenience features last. Scores returned as 0–100%.
    """

    # 1) Hard filters
    allowed_body = set(user.purchase_basics.body_types)
    allowed_fuel = set(user.purchase_basics.fuel_types)
    budget = user.purchase_basics.budget

    def passes_filters(car: CarSpec) -> bool:
        return (
            car["price"] <= budget
            and (car["bodyType"] in allowed_body)
            and (car["fuelType"] in allowed_fuel)
        )

    filtered: List[CarSpec] = [c for c in CATALOG if passes_filters(c)]
    if not filtered:
        return []

    # 2) Priority weights (normalize to sum=1), but enforce safety emphasis
    base_weights: Dict[Priority, float] = {
        Priority.cheap_to_run: 0.9,
        Priority.features: 0.6,       # intentionally lower than safety/reliability
        Priority.performance: 0.7,
        Priority.safety: 1.6,         # safety emphasized
        Priority.mileage: 0.9,
    }
    # Respect user priorities but cap features to avoid overshadowing safety/reliability
    for i, p in enumerate(user.needs_priorities.priorities):
        bump = 0.4 - 0.05 * i
        base_weights[p] += bump

    # Cap features weight to remain below safety
    base_weights[Priority.features] = min(base_weights[Priority.features], base_weights[Priority.safety] * 0.7)

    total_w = sum(base_weights.values())
    weights = {k: v / total_w for k, v in base_weights.items()}

    # 3) Normalization denominators (avoid div-by-zero)
    max_price = max(c["price"] for c in filtered)
    max_mileage = max(c["mileage_kmpl"] for c in filtered)
    max_power = max(c["performance_power_hp"] for c in filtered)
    max_music = max(c.get("music_quality", 1) for c in filtered)
    max_reliability = max(c.get("reliability_score", 1) for c in filtered)  # 1–5 scale
    max_mileage = max(max_mileage, 1e-9)
    max_power = max(max_power, 1e-9)
    max_music = max(max_music, 1e-9)
    max_reliability = max(max_reliability, 1e-9)

    # 4) Sub-scores (0–1)
    def score_cheap_to_run(car):
        return 1.0 - (car["price"] / max_price)

    def score_features(car):
        feats = car.get("features", {})
        present = sum([
            1 if feats.get("rear_camera") else 0,
            1 if feats.get("cruise_control") else 0,
            1 if feats.get("wireless_android_auto") else 0
        ])
        return present / 3.0

    def score_performance(car):
        return car["performance_power_hp"] / max_power

    def score_safety(car):
        base = min(car.get("safety_airbags", 0), 6) / 6.0
        esp = 0.2 if car.get("has_esp") else 0.0
        return min(1.0, base + esp)

    def score_mileage(car):
        return car["mileage_kmpl"] / max_mileage

    def score_reliability(car):
        # Normalize reliability proxy (1–5) to 0–1
        return car.get("reliability_score", 3) / max_reliability

    # 5) Bonuses/Penalties (kept small so they don’t overpower safety/reliability)
    feature_bonus_map = {
        FeaturePriority.driver_safety: lambda car: (1.0 if car.get("safety_airbags", 0) >= 6 else 0.0) * 0.15
                                                  + (0.15 if car.get("has_esp") else 0.0),
        FeaturePriority.passenger_features: lambda car: (0.08 if car.get("features", {}).get("rear_camera") else 0.0),
        FeaturePriority.driving_convenience: lambda car: (0.08 if car.get("features", {}).get("cruise_control") else 0.0),
        FeaturePriority.low_maintenance: lambda car: 0.1 if car.get("reliability_score", 3) >= 4 else 0.0,
        FeaturePriority.comfort_features: lambda car: 0.05 if car.get("features", {}).get("wireless_android_auto") else 0.0,
    }

    def feature_bonus(car):
        # Cap total bonus to avoid overshadowing safety/reliability
        total = sum(feature_bonus_map[fp](car) for fp in user.needs_priorities.feature_priority)
        return min(total, 0.25)

    def music_alignment(car):
        return (user.other_preferences.music_importance / 10.0) * (car.get("music_quality", 1) / max_music)

    def brand_alignment_penalty(car):
        diff = abs(user.needs_priorities.brand_value - car.get("brand_value", 1)) / 3.0
        return diff

    # 6) Final score → percentage with clamping
    ranked: List[Tuple[float, Dict[str, object]]] = []
    for car in filtered:
        s = {
            "cheap_to_run": score_cheap_to_run(car),
            "features": score_features(car),
            "performance": score_performance(car),
            "safety": score_safety(car),
            "mileage": score_mileage(car),
            "reliability": score_reliability(car),
            "feature_bonus": feature_bonus(car),
            "music_alignment": music_alignment(car),
            "brand_alignment": brand_alignment_penalty(car),
        }

        core = (
            weights[Priority.safety]       * s["safety"] +
            s["reliability"] +  # reliability is first-class; weight = 1 implicitly
            weights[Priority.mileage]      * s["mileage"] +
            weights[Priority.cheap_to_run] * s["cheap_to_run"] +
            weights[Priority.performance]  * s["performance"] +
            weights[Priority.features]     * s["features"]
        )

        bonus = s["feature_bonus"] + 0.03 * s["music_alignment"]  # smaller than before
        penalty = 0.04 * s["brand_alignment"]                      # small penalty

        final_0_1 = max(0.0, min(1.0, core + bonus - penalty))
        final_pct = round(final_0_1 * 100.0, 2)

        reason = build_reason(s, weights, car, user)

        ranked.append((
            final_0_1,
            {
                "mmv": car["mmv"],
                "score_percent": final_pct,
                "reason": reason,
                "breakdown": {
                    **{k: round(v, 4) for k, v in s.items()},
                    "weights": {k.value: round(v, 4) for k, v in weights.items()},
                    "core_score_0_1": round(core, 4),
                    "bonus_0_1": round(bonus, 4),
                    "penalty_0_1": round(penalty, 4)
                },
                "specs": car
            }
        ))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in ranked[:top_n]]
