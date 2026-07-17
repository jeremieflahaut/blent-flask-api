STATUT_EN_ATTENTE = "en_attente"
STATUT_VALIDEE = "validée"
STATUT_EXPEDIEE = "expédiée"
STATUT_ANNULEE = "annulée"

STATUTS = (
    STATUT_EN_ATTENTE,
    STATUT_VALIDEE,
    STATUT_EXPEDIEE,
    STATUT_ANNULEE,
)

# Machine à états des commandes : pour chaque statut, les cibles autorisées.
# Un tuple vide signale un statut terminal.
TRANSITIONS = {
    STATUT_EN_ATTENTE: (STATUT_VALIDEE, STATUT_ANNULEE),
    STATUT_VALIDEE: (STATUT_EXPEDIEE, STATUT_ANNULEE),
    STATUT_EXPEDIEE: (),
    STATUT_ANNULEE: (),
}
