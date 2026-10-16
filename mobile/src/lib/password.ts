export const MIN_PASSWORD_LENGTH = 8;
export const PASSWORD_REQUIREMENTS = 'New passwords need 8+ characters with uppercase, lowercase, a number and a special character.';

export function passwordIssue(password: string, confirmation: string): string {
  if (password.length < MIN_PASSWORD_LENGTH) return `Use at least ${MIN_PASSWORD_LENGTH} characters.`;
  if (!/[a-z]/.test(password)) return 'Add at least one lowercase letter.';
  if (!/[A-Z]/.test(password)) return 'Add at least one uppercase letter.';
  if (!/[0-9]/.test(password)) return 'Add at least one number.';
  if (!/[^A-Za-z0-9]/.test(password)) return 'Add at least one special character.';
  if (password !== confirmation) return 'Passwords do not match.';
  return '';
}
