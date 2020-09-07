export function setID(data) {
  sessionStorage.setItem('id', data);
}

export function getID() {
  return sessionStorage.getItem('id');
}

export function deleteID() {
  sessionStorage.removeItem('id')
}

export function setModel(data){
  sessionStorage.setItem('model', JSON.stringify(data));
}

export function getModel() {
  return JSON.parse(sessionStorage.getItem('model'));
}

export function deleteModel() {
  sessionStorage.removeItem('model')
}

