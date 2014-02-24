//Meteor.subscribe("submissions");

Template.submissionsList.helpers({
    submissions: function() { return Submissions.find(); }
});
