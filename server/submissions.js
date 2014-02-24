//Submissions = new Meteor.Collection("submissions");

Meteor.publish("submissions", function(options) {
    return Submissions.find({}, options);
});
