
document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("sr-edit-modal");
    const form = document.getElementById("sr-edit-form");
    const closeButton = document.getElementById("sr-close-modal");
    const nameText = document.getElementById("sr-edit-name");
    const favoriteInput = document.getElementById("sr-edit-favorite");
    const modalImage = document.getElementById("sr-edit-image");

    if (!modal || !form) return;

    const csrfToken = form.querySelector(
        '[name="csrfmiddlewaretoken"]'
    ).value;

    let activeButton = null;

    // MEMBUKA POPUP EDIT
    document.querySelectorAll(".sr-btn-edit").forEach(button => {

        button.addEventListener("click", function () {

            activeButton = button;

            nameText.textContent = button.dataset.name;

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
                    'input[name="meal_category"][value="uncategorized"]'
                ).checked = true;
            }

            // Tampilkan foto resep jika tersedia
            if (modalImage) {
                const card = button.closest(".sr-card");
                const cardImage = card.querySelector(".sr-image img");

                if (cardImage) {
                    modalImage.src = cardImage.src;
                    modalImage.hidden = false;
                } else {
                    modalImage.removeAttribute("src");
                    modalImage.hidden = true;
                }
            }

            modal.hidden = false;
        });
    });


    // MENUTUP POPUP
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


    // UPDATE KE DATABASE DJANGO
    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        if (!activeButton) return;

        const category = form.querySelector(
            'input[name="meal_category"]:checked'
        ).value;

        const favorite = favoriteInput.checked;

        const saveButton = form.querySelector(".sr-save-btn");
        saveButton.disabled = true;

        try {
            console.log("Update URL:", activeButton.dataset.updateUrl);
            const response = await fetch(
                activeButton.dataset.updateUrl,
                {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken
                    },
                    mode: "same-origin",
                    body: new URLSearchParams({
                        meal_category: category,
                        is_favorite: String(favorite)
                    })
                }
            );

            if (!response.ok) {
                throw new Error("Update gagal");
            }

            // Reload untuk mengambil data terbaru dari Django
            window.location.reload();

        } catch (error) {
            alert("Gagal menyimpan perubahan.");
            saveButton.disabled = false;
        }
    });


    // DELETE DARI DATABASE DJANGO
    document.querySelectorAll(".sr-btn-delete").forEach(button => {

        button.addEventListener("click", async function () {

            const confirmed = confirm(
                "Are you sure you want to delete this saved recipe?"
            );

            if (!confirmed) return;

            button.disabled = true;

            try {
                const response = await fetch(
                    button.dataset.deleteUrl,
                    {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": csrfToken
                        },
                        mode: "same-origin"
                    }
                );

                if (!response.ok) {
                    throw new Error("Delete gagal");
                }

                window.location.reload();

            } catch (error) {
                alert("Gagal menghapus resep.");
                button.disabled = false;
            }
        });
    });

    // Add or remove a recipe from the meal plan draft
    document.querySelectorAll(".sr-btn-add-to-plan").forEach(button => {
        button.addEventListener("click", async function () {
            button.disabled = true;

            try {
                const response = await fetch(button.dataset.toggleUrl, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken
                    },
                    mode: "same-origin"
                });

                const result = await response.json().catch(() => ({}));

                if (!response.ok) {
                    throw new Error(
                        result.message || "Could not update the meal plan."
                    );
                }

                button.dataset.added = String(result.added);
                button.textContent = result.added
                    ? "Added to Plan"
                    : "Add to Plan";
                button.classList.toggle("is-added", result.added);
            } catch (error) {
                const errorMessage =
                    document.getElementById("sr-plan-error");

                if (errorMessage) {
                    errorMessage.textContent =
                        error.message || "Could not connect to the server.";
                } else {
                    alert(error.message || "Could not update the meal plan.");
                }
            } finally {
                button.disabled = false;
            }
        });
    });

    // Save the selected recipes and create the plan
    const saveMealplanButton =
        document.getElementById("sr-save-mealplan");
    const savePlanModal =
        document.getElementById("sr-save-plan-modal");
    const cancelSavePlanButton =
        document.getElementById("sr-cancel-save-plan");
    const confirmSavePlanButton =
        document.getElementById("sr-confirm-save-plan");
    const savePlanError =
        document.getElementById("sr-plan-error");

    function closeSavePlanModal() {
        if (savePlanModal) {
            savePlanModal.hidden = true;
        }
    }

    if (saveMealplanButton && savePlanModal) {
        saveMealplanButton.addEventListener("click", async function () {
            if (savePlanError) {
                savePlanError.textContent ="";
            }

            savePlanModal.hidden = false;
            confirmSavePlanButton.focus();
        });

        cancelSavePlanButton.addEventListener(
            "click",
            closeSavePlanModal
        );
        savePlanModal.addEventListener("click", function (event) {
            if (event.target === savePlanModal){
                closeSavePlanModal();
            }
        });
        document.addEventListener("keydown", function(event) {
            if ( event.key === "Escape" && !savePlanModal.hidden) {
                closeSavePlanModal();
            }
        });

        confirmSavePlanButton.addEventListener(
            "click",
            async function () {
                confirmSavePlanButton.disabled = true;
                confirmSavePlanButton.textContent = "Saving...";

                try {
                    const response = await fetch(
                        saveMealplanButton.dataset.saveUrl,
                        {
                            method: "POST",
                            headers: {"X-CSRFToken": csrfToken},
                            mode: "same-origin"
                        }
                    );

                    const result = await response.json().catch(() => ({}));

                    if (!response.ok) {
                        throw new Error(result.message || "Could not save the plan.");
                    }

                    window.location.href = result.redirect_url;
                } catch (error) {
                    closeSavePlanModal();

                    if (savePlanError) {
                        savePlanError.textContent = error.message || "Could not connect to the server.";
                    }

                    confirmSavePlanButton.disabled = false;
                    confirmSavePlanButton.textContent = "Yes, Save Plan";
                }
            }
        )
    }
});
