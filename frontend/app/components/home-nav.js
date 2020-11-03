import Component from '@glimmer/component';
import { inject as service } from '@ember/service';

export default class HomeNavComponent extends Component {
  @service session;

  get isAuthenticated() {
    return this.session.isAuthenticated;
  }

  get user() {
    return this.session.data.authenticated.profile.nickname;
  }

}
