export default class UserInfo {
    constructor(data) {
      this._name = document.querySelector(data.name);
      this._job = document.querySelector(data.job);
      this._userId = '';
      this._userData = {};
    }

    getUserInfo() {
      this._userData.name = this._name.textContent;
      this._userData.job = this._job.textContent;
      return this._userData;
    }

    setUserInfo(userData) {
      // поля из полученных данных api
      this._name.textContent = userData.lastname_and_initials;
      this._job.textContent = userData.job_position;
      this._userId = userData.id;
    }
  }
