
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



    const deleteDialog = document.getElementById("sr-delete-dialog");
    const deleteCancel = document.getElementById("sr-delete-cancel");
    const deleteConfirm = document.getElementById("sr-delete-confirm");
    const deleteRecipeName = document.getElementById("sr-delete-recipe-name");
    const deleteError = document.getElementById("sr-delete-error");

    let selectedDeleteButton = null;
    let deleteInProgress = false;

    document.querySelectorAll(".sr-btn-delete").forEach(button => {
        button.addEventListener("click", function () {

            selectedDeleteButton = button;

            const card = button.closest(".sr-card");
            const recipeName = card.querySelector("h3").textContent.trim();

            deleteRecipeName.textContent = recipeName;
            deleteError.hidden = true;

            deleteDialog.showModal();
        });
    });

    deleteCancel.addEventListener("click", function () {
        deleteDialog.close();
    });

    deleteDialog.addEventListener("click", function (event) {
        if (event.target === deleteDialog && !deleteInProgress) {
            deleteDialog.close();
        }
    });

    deleteDialog.addEventListener("cancel", function (event) {
        if (deleteInProgress) {
            event.preventDefault();
        }
    });

    deleteDialog.addEventListener("close", function () {
        selectedDeleteButton = null;
    });

    deleteConfirm.addEventListener("click", async function () {

        if (!selectedDeleteButton || deleteInProgress) return;

        const button = selectedDeleteButton;
        deleteInProgress = true;

        button.disabled = true;
        deleteCancel.disabled = true;
        deleteConfirm.disabled = true;
        deleteConfirm.textContent = "Deleting...";
        deleteError.hidden = true;

        try {
            const response = await fetch(
                button.dataset.deleteUrl,
                {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken
                    },
                    credentials: "same-origin"
                }
            );

            if (!response.ok) {
                throw new Error("Delete gagal");
            }

            deleteDialog.close();
            window.location.reload();

        } catch (error) {
            deleteError.hidden = false;

        } finally {
            deleteInProgress = false;
            button.disabled = false;
            deleteCancel.disabled = false;
            deleteConfirm.disabled = false;
            deleteConfirm.textContent = "Confirm Delete";
        }
    });


});
