const THEME_KEY = "app_theme";
let mediaListener = null;

export function applyTheme(mode) {
  const root = document.documentElement;

  if (mediaListener) {
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .removeEventListener("change", mediaListener);
    mediaListener = null;
  }

  root.classList.remove("theme-dark", "theme-light");

  const setDark = (on) => root.classList.toggle("theme-dark", !!on);
  const setLight = (on) => root.classList.toggle("theme-light", !!on);

  if (mode === "dark") {
    setDark(true);
    setLight(false);
    localStorage.setItem(THEME_KEY, "dark");
    return;
  }

  if (mode === "light") {
    setLight(true);
    setDark(false);
    localStorage.setItem(THEME_KEY, "light");
    return;
  }

  const mq = window.matchMedia("(prefers-color-scheme: dark)");
  setDark(mq.matches);
  setLight(!mq.matches);
  localStorage.setItem(THEME_KEY, "system");

  mediaListener = (e) => {
    setDark(e.matches);
    setLight(!e.matches);
  };
  mq.addEventListener("change", mediaListener);
}

export function getSavedTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === "dark" || saved === "light" || saved === "system") {
    return saved;
  }
  return "system";
}

export function initTheme() {
  applyTheme(getSavedTheme());
}