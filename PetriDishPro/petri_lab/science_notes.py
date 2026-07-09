CLAIM_BOUNDARY = (
    "Educational and exploratory simulation only. Not clinical, diagnostic, "
    "wet-lab validated, epidemiological, or treatment guidance."
)

MODEL_NOTES = {
    "growth": "Local growth uses a simplified Monod-like nutrient saturation and logistic crowding term.",
    "motility": "Motility is approximated by a conservative neighborhood diffusion operator.",
    "toxicity": "Toxin/antibiotic effect is represented as a sensitivity scalar, not a pharmacological model.",
    "predation": "Predator-prey coupling transfers a fraction of prey biomass into predator growth.",
    "cellular": "Cellular presets are phenotype-like agents, not calibrated cell-line models.",
}
