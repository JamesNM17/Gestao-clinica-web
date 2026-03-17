function toggleTheme() {
    document.body.classList.toggle("dark");

    // salva a preferência
    const isDark = document.body.classList.contains("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");}

// carrega a preferência ao abrir o site
window.onload = () => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
        document.body.classList.add("dark");
    }
};

