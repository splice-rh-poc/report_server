App = Ember.Application.create();

App.ApplicationView = Ember.View.extend({
	templateName: 'application'
});

App.ApplicationController = Ember.Controller.extend();

App.Router.map(function(match) {
  match('/').to('index');
});

App.IndexRoute = Ember.Route.extend({
  renderTemplates: function() {
    this.render('foo-template');
  }
});