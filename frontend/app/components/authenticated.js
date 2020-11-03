import Component from '@glimmer/component';
import { inject as service } from '@ember/service';
import { action } from '@ember/object';
import { tracked } from '@glimmer/tracking';

export default class AuthenticatedComponent extends Component {
  @service session;

  get isAuthenticated() {
    return this.session.isAuthenticated;
  }

  @action
  login() {
    // Check out the docs for all the options:
    // https://auth0.com/docs/libraries/auth0js/v9#webauth-authorize-
    const authOptions = {
      responseType: 'token',
      audience: 'agency_api',
      redirectUri: 'http://localhost:4200/'
    };

    this.session.authenticate('authenticator:auth0-universal', authOptions, (err, email) => {
      if (err) {
        console.log(err);
      }
    });
  }

  @action
  logout() {
    this.session.invalidate();
  }
}
