// Browser checks (the server repeats the same rules in app.py).

// Show a list of messages in the red box next to the form
function showErrors(form, errors) {
  const box = (form.closest(".scope") || form).querySelector(".errors");
  box.innerHTML = errors.map(e => "<li>" + e + "</li>").join("");
  box.hidden = errors.length === 0;
}

function checkRegister(f) {
  const errors = [];
  if (f.name.value.trim() === "") errors.push("Name is required");
  const email = f.email.value.trim();
  if (email === "") errors.push("Email is required");
  else if (!/^[^@\s]+@[^@\s]+$/.test(email)) errors.push("Email must contain @ (like name@example.com)");
  if (f.password.value === "") errors.push("Password is required");
  if (f.confirm_password.value === "") errors.push("Confirm password is required");
  if (f.password.value && f.confirm_password.value && f.password.value !== f.confirm_password.value)
    errors.push("Passwords do not match");
  return errors;
}

function checkLogin(f) {
  const errors = [];
  if (f.email.value.trim() === "") errors.push("Email is required");
  if (f.password.value === "") errors.push("Password is required");
  return errors;
}

function checkTodo(f) {
  const title = f.title.value;
  if (title.trim() === "") return ["Title is required"];
  if (title.length > 200) return ["Title is too long (200 characters at most)"];
  return [];
}

// Bonus: check the chosen image (the server checks again, also the real file content)
const MAX_IMAGE = 2 * 1024 * 1024;
function imageErrors(f) {
  const file = f.elements.image && f.elements.image.files[0];
  if (!file) return [];
  if (!/^image\/(jpeg|png|gif|webp)$/.test(file.type)) return ["Image must be a JPG, PNG, GIF or WEBP file"];
  if (file.size > MAX_IMAGE) return ["Image is too big (2 MB at most)"];
  return [];
}

function checkBook(f) {
  const title = f.elements.title.value.trim();
  const price = f.elements.price.value.trim();
  const errors = [];
  if (title === "") errors.push("Title is required");
  else if (title.length > 150) errors.push("Title is too long (150 characters at most)");
  if (price === "") errors.push("Price is required");
  else if (!/^\d{1,8}(\.\d{1,2})?$/.test(price)) errors.push("Price must be a number like 12.50");
  if (f.elements.author_id.value === "") errors.push("Author is required");
  return errors.concat(imageErrors(f));
}

function checkAuthor(f) {
  const name = f.elements.name.value.trim();
  const country = f.elements.country.value.trim();
  const errors = [];
  if (name === "") errors.push("Name is required");
  else if (name.length > 100) errors.push("Name is too long (100 characters at most)");
  if (country === "") errors.push("Country is required");
  else if (country.length > 50) errors.push("Country is too long (50 characters at most)");
  return errors.concat(imageErrors(f));
}

const checks = { register: checkRegister, login: checkLogin, todo: checkTodo,
                 book: checkBook, author: checkAuthor };

// Every form with data-form="..." is checked before it is sent
document.querySelectorAll("form[data-form]").forEach(form => {
  form.addEventListener("submit", event => {
    const errors = checks[form.dataset.form](form);
    if (errors.length > 0) {
      event.preventDefault();   // nothing is sent
      showErrors(form, errors);
    }
  });
});

// "Are you sure?" before deleting
document.querySelectorAll("form[data-confirm]").forEach(form => {
  form.addEventListener("submit", event => {
    if (!confirm(form.dataset.confirm)) event.preventDefault();
  });
});

// Light / dark mode button. The choice is remembered in the browser (localStorage).
const themeButton = document.getElementById("theme-toggle");

function currentTheme() {
  // the chosen theme, or the system setting if nothing was chosen yet
  return document.documentElement.dataset.theme ||
    (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
}

function updateThemeButton() {
  themeButton.textContent = currentTheme() === "dark" ? "☀️" : "🌙";   // shows what you switch to
}

themeButton.addEventListener("click", () => {
  const next = currentTheme() === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("theme", next); } catch (e) {}
  updateThemeButton();
});

updateThemeButton();
