$(document).ready(function(){
	var current;

	$("#playlists").append('<h3 style="text-align: center;">Select Secret Playlist, ' + user.id + '</h3>');
	for(var p in playlists.items){
		if(playlists.items[p].public == false && playlists.items[p].collaborative == false){
			$("#playlists").append('<div class="spotDiv"><a id="playlist_' + p + '" class="addButton" href="#" data-toggle="modal" data-target="#playlistModal"><span class="glyphicon glyphicon-plus"></span></a><iframe class="spotFrame" src="https://embed.spotify.com/?uri=' + encodeURIComponent(playlists.items[p].uri) + '&theme=black&view=coverart" width="350" height="80" frameborder="0" allowtransparency="true"></iframe></div>');

		}
	}

    $('#playlistModal').on('shown.bs.modal', function (event) {
	    console.log($(event.relatedTarget)[0]);
            current = playlists.items[parseInt($(event.relatedTarget)[0].id.replace('playlist_', ''))];
            $("#publicName").val(current.name + " - Public");
            $("#publicDescription").val("");
    });


            $("#createPlaylistButton").click(function(){
                    if($("#publicName").val() != ""){
                            $.ajax({
                                    url: "/create",
                                    type: "POST",
                                    dataType: "json",
                                    contentType: "application/json; charset=utf-8",
                                    data: JSON.stringify({
                                            secret: current,
                                            name: $("#publicName").val(),
                                            user: user,
                                            access: access
                                    }),
                                    success: function(data){
			            	window.location.replace('http://adventify.davidlips.onl/playlist/'+ data.id);					    
                                    },
                                    error: function(data){
                                            console.log(data);
                                    }
                            });
                    }

            });

});
