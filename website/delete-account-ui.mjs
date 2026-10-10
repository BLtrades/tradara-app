import { deleteTradaraAccount } from './delete-account.mjs';
const form = document.getElementById('deletion-form');
const status = document.getElementById('status');
const button = document.getElementById('submit');
const email = document.getElementById('email');
const password = document.getElementById('password');
const confirmation = document.getElementById('confirmation');
form.addEventListener('submit', async event => {
  event.preventDefault();
  button.disabled = true;
  status.className = 'status';
  status.textContent = 'Checking your account…';
  try {
    await deleteTradaraAccount(email.value, password.value, confirmation.value);
    form.reset();
    form.remove();
    status.className = 'status success';
    status.textContent = 'Your Tradara account has been deleted.';
  } catch (error) {
    password.value = '';
    status.className = 'status error';
    status.textContent = error instanceof Error ? error.message : 'Could not complete deletion. Your account remains active.';
    button.disabled = false;
  }
});
