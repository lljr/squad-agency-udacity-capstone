import Route from '@ember/routing/route';
import RSVP from 'rsvp';
import ApplicationRouteMixin from 'ember-simple-auth-auth0/mixins/application-route-mixin';

export default Route.extend(ApplicationRouteMixin, {
  beforeSessionExpired() {
    // Do custom async logic here, e.g. notify
    // the user that they are about to be logged out.

    return RSVP.resolve();
  }

  // Do other application route stuff here. All hooks provided by
  // ember-simple-auth's ApplicationRouteMixin, e.g. sessionInvalidated(),
  // are supported and work just as they do in basic ember-simple-auth.
});
