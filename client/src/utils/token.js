export function setToken(data) {
  sessionStorage.setItem('id', data);
}

export function getToken() {
  return sessionStorage.getItem('id');
}

export function deleteToken() {
  sessionStorage.removeItem('id')
}