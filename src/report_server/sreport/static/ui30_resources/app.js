App = Ember.Application.create();

App.ApplicationView = Ember.View.extend({
	templateName: 'application'
});

App.ApplicationController = Ember.Controller.extend();

App.FooController = Ember.ObjectController.extend();
App.FooView = Ember.View.extend({
	templateName: 'foo-template'
})

App.Router = Ember.Router.extend({
	enableLoggin: true,
	root: Ember.Route.extend({
		index: Ember.Route.extend({
			route: '/',
			connectOutlets: function(router) {
				router.get('applicationController').connectOutlet('foo');
			}
		})
	})
});