export function setID(data) {
  sessionStorage.setItem("id", data);
}

export function getID() {
  return sessionStorage.getItem("id");
}

export function deleteID() {
  sessionStorage.removeItem("id");
}

export function setModel(data) {
  sessionStorage.setItem("model", JSON.stringify(data));
}

export function getModel() {
  return JSON.parse(sessionStorage.getItem("model"));
}

export function deleteModel() {
  sessionStorage.removeItem("model");
}

export function setTeacher(data) {
  sessionStorage.setItem("teacherType", JSON.stringify(data));
}

export function getTeacher() {
  return JSON.parse(sessionStorage.getItem("teacherType"));
}

export function deleteTeacher() {
  sessionStorage.removeItem("teacherType");
}

export function setSetting(data) {
  sessionStorage.setItem("setting", JSON.stringify(data));
}

export function getSetting() {
  return JSON.parse(sessionStorage.getItem("setting"));
}

export function deleteSetting() {
  sessionStorage.removeItem("setting");
}
