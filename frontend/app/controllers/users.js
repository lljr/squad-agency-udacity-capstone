import Controller from '@ember/controller';
import { inject as service } from '@ember/service';

export default class UsersController extends Controller {
  @service session;

  get token() {
    this.session.data.authenticated.accessToken;
  }

}
