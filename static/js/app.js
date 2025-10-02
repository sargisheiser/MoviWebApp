document.addEventListener("DOMContentLoaded", () => {
    const userForm = document.getElementById("add-user-form");
    if (userForm) {
        userForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("new-username").value;
            const res = await fetch("/api/users", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({name})
            });
            if (res.ok) location.reload();
        });
    }

    document.querySelectorAll(".btn-delete-user").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const id = e.target.closest("li").dataset.id;
            const res = await fetch(`/api/users/${id}`, {method: "DELETE"});
            if (res.ok) location.reload();
        });
    });

    const movieForm = document.getElementById("add-movie-form");
    if (movieForm) {
        movieForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const userId = movieForm.dataset.userId;
            const title = document.getElementById("new-movie-title").value;
            const res = await fetch(`/api/users/${userId}/movies`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({title})
            });
            if (res.ok) location.reload();
        });
    }

    document.querySelectorAll(".btn-delete-movie").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const id = e.target.closest("li").dataset.id;
            const res = await fetch(`/api/movies/${id}`, {method: "DELETE"});
            if (res.ok) location.reload();
        });
    });

    document.querySelectorAll(".btn-update-movie").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            const li = e.target.closest("li");
            const id = li.dataset.id;
            const newTitle = li.querySelector(".update-title").value;
            if (!newTitle) return;

            const res = await fetch(`/api/movies/${id}`, {
                method: "PUT",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({title: newTitle})
            });
            if (res.ok) location.reload();
        });
    });
});


