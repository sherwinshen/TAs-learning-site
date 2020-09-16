import service from '../utils/interceptor';

export function Learning(data) {
  return service.request({
    url: '/learning',
    method: 'post',
    data,
  });
}

export function Processing(data) {
  return service.request({
    url: '/processing',
    method: 'post',
    data,
  });
}

export function Result(data) {
  return service.request({
    url: '/result',
    method: 'post',
    data,
  });
}

export function Delete(data) {
  return service.request({
    url: '/delete',
    method: 'post',
    data,
  });
}

export function GetResult(data) {
  return service.request({
    url: '/getResult',
    method: 'post',
    data,
  });
}

export function GetMiddle(data) {
  return service.request({
    url: '/getMiddle',
    method: 'post',
    data,
  });
}