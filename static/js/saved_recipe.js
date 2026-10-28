document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("sr-edit-modal");
    const closeButton = document.getElementById("sr-close-modal");
    const nameText = document.getElementById("sr-edit-name");
    const modalImage = document.getElementById("sr-edit-image");
    const favoriteInput = document.getElementById("sr-edit-favorite");
    const form = document.getElementById("sr-edit-form");

    let activeCard = null;
    let activeButton = null;

    document.querySelectorAll(".sr-btn-edit").forEach(button => {
        button.addEventListener("click", function () {
            activeButton = button;
            activeCard = button.closest(".sr-card");

            nameText.textContent = button.dataset.name;
            
            // Ambil foto dari card yang sedang diedit
            const cardImage = activeCard.querySelector(".sr-image img");

            if (cardImage) {
                modalImage.src = cardImage.src;
                modalImage.alt = button.dataset.name;
                modalImage.hidden = false;
            } else {
                modalImage.removeAttribute("src");
                modalImage.alt = "";
                modalImage.hidden = true;
            }


            favoriteInput.checked =
                button.dataset.favorite === "true";

            const category = button.dataset.category;
            const radio = form.querySelector(
                `input[name="meal_category"][value="${category}"]`
            );

            if (radio) {
                radio.checked = true;
            } else {
                form.querySelector(
                    'input[value="uncategorized"]'
                ).checked = true;
            }

            modal.hidden = false;
        });
    });

    function closeModal() {
        modal.hidden = true;
    }

    closeButton.addEventListener("click", closeModal);

    modal.addEventListener("click", function (event) {
        if (event.target === modal) closeModal();
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") closeModal();
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const category = form.querySelector(
            'input[name="meal_category"]:checked'
        ).value;

        const favorite = favoriteInput.checked;

        // Perbarui tampilan sementara
        activeCard.querySelector(".sr-category").textContent =
            category.charAt(0).toUpperCase() + category.slice(1);

        const titleRow = activeCard.querySelector(".sr-title-row");
        let heart = titleRow.querySelector(".sr-heart");

        if (favorite && !heart) {
            heart = document.createElement("span");
            heart.className = "sr-heart";
            heart.textContent = "♥";
            titleRow.appendChild(heart);
        } else if (!favorite && heart) {
            heart.remove();
        }

        activeButton.dataset.category = category;
        activeButton.dataset.favorite = String(favorite);

        closeModal();
    });
});
