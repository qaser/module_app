import * as constant from './utils/constants.js';

function renderLoading(isLoading) {
  if (isLoading) {
    constant.loadingScreen.classList.add('loader_disactive');
  }
}

export { renderLoading };
