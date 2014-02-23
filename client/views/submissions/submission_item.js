Template.submissionItem.helpers({
    domain: function() {
        var a = document.createElement("a");
        a.href = this.bandcamp_uri;
        return a.hostname;
    }
});
