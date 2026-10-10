export const MIN_PASSWORD_LENGTH = 6;

export function passwordIssue(password: string, confirmation: string): string {
  if (password.length < MIN_PASSWORD_LENGTH) return `Use at least ${MIN_PASSWORD_LENGTH} characters.`;
  if (password !== confirmation) return 'Passwords do not match.';
  return '';
}
