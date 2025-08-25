const dialog = document.querySelector("#nav-modal");
const showButton = document.querySelector("#nav-modal-open");
const closeButton = document.querySelector("#nav-modal-close");

dialog.addEventListener("click", (event) => {
  if (event.target === dialog) {
    dialog.close();
  }
});

// "Show the dialog" button opens the dialog modally
showButton.addEventListener("click", () => {
  dialog.showModal();
});

// "Close" button closes the dialog
closeButton.addEventListener("click", () => {
  dialog.close();
});
