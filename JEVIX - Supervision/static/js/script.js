// Attend que toute la page HTML soit chargée
document.addEventListener("DOMContentLoaded", function () {


    // Récupère le bouton de déconnexion
    const logoutButton = document.querySelector(".btn-danger");


    // Vérifie si le bouton existe sur la page
    if (logoutButton) {

        logoutButton.addEventListener("click", function (event) {

            // Demande confirmation avant la déconnexion
            const confirmation = confirm(
                "Voulez-vous vraiment vous déconnecter ?"
            );

            // Annule la déconnexion si l'utilisateur refuse
            if (!confirmation) {
                event.preventDefault();
            }

        });

    }


    // Récupère tous les boutons de suppression
    const deleteButtons = document.querySelectorAll(".btn-delete");


    // Parcourt tous les boutons de suppression
    deleteButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            // Demande confirmation avant la suppression
            const confirmation = confirm(
                "Voulez-vous vraiment supprimer cet administrateur ?"
            );

            // Annule la suppression si l'utilisateur refuse
            if (!confirmation) {
                event.preventDefault();
            }

        });

    });


    // Récupère les messages ayant la classe "alert"
    const alerts = document.querySelectorAll(".alert");


    // Parcourt les messages d'alerte
    alerts.forEach(function (alert) {

        // Cache le message après 4 secondes
        setTimeout(function () {

            alert.style.display = "none";

        }, 4000);

    });

    // Récupère tous les boutons de résolution d'alerte
    const resolveButtons = document.querySelectorAll(".btn-resoudre");

resolveButtons.forEach(function (button) {

    button.addEventListener("click", function (event) {

        const confirmation = confirm(
            "Voulez-vous vraiment marquer cette alerte comme résolue ?"
        );

        if (!confirmation) {
            event.preventDefault();
        }

    });

});
});