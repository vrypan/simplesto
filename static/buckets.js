edit_mode = false ;
api_endpoint = '/api' ;

function show_user_buckets( secret ) {
	var url = api_endpoint+'/bucket/'+secret+'?jsoncallback=?' ;
	$.getJSON(url, function(json){
		$('#status').text('getting user buckets');
		buckets = json;
		$("#data").html('');
		$("#data").append('<h2>my buckets</h2>\n');
		$("#data").append('<table id="myBuckets" class="bucket"></table>');

		var html = '' ;
		html = html + '<tr><th>name</th><th>description</th><th>public?</th>' ;
		html = html + '<th>last update</th><th>secret</th>' ;
		html = html + '<th class="actions"><input type="button" id="new_bucket_button" value="create bucket"/></tr>' ;
		$('#myBuckets').append(html) ;
		
		html = '<tr id="new_bucket_form">' ;
		html = html + '<td><input type="text" id="new_bucket_name"/ style="width:100%" ></td>' ;
		html = html + '<td><input type="text" id="new_bucket_description" style="width:100%" /></td>';
		html = html + '<td><input type="text" value="No" id="new_bucket_is_public" style="width:100%" /></td>';
		html = html + '<td colspan="2"></td>';
		html = html + '<td class="actions"><input type="button" id="new_bucket_save_button" value="create" /> <input type="button" id="new_bucket_cancel_button" value="cancel" /></td>\n';
		html = html + '</tr>\n' ;
		$('#myBuckets').append(html) ;

		for(var i=0,len=buckets.length; bucket=buckets[i],i<len; i++){
			html = '' ;
			if (bucket['is_public']==true) {
				var is_pub = 'Yes'
			} else {
				var is_pub = 'No';
			}
			html = html + '<tr class="row"><td class="name">'+bucket['name']+'</td>';
			html = html + '<td class="description">'+bucket['description']+'</td>' ;
			html = html + '<td class="is_pub bool">'+ is_pub +'</td>' ;
			html = html + '<td class="date upd_date">'+bucket['upd_date']+'</td>' ;
			html = html + '<td class="token">'+bucket['auth_token']+'</td>' ;
			html = html + '<td class="actions">';
			html = html + '<a href="#" class="button delete_bucket">delete</a></td></tr>' ;
			
			$('#myBuckets').append(html);
		}
		
		$(".name").click(function(e){
			var target = $(e.currentTarget);
			var data_row = target.parents('tr') ;
			var bucket_name = data_row.children('.name').text() ;
			var secret = data_row.children('.token').text() ;
			document.location.href= '/gui/bucket/'+secret+'/'+bucket_name+'/item';
			//show_bucket_contents(bucket_name, secret) ;
		})
		$(".description").click(function(e){
			if (edit_mode == true) {
				return ;
			}
			edit_bucket(e);
		}) ;
		$(".is_pub").click(function(e){
			if (edit_mode == true) {
				return ;
			}
			edit_bucket(e);
		}) ;
		
		function edit_bucket(e){
			var target = $(e.currentTarget);
			var old_value = target.html();
			edit_mode = true ;
			var data_row = target.parents('tr') ;
			var bucket_name = data_row.children('.name').text() ;
			var bucket_secret = data_row.children('.token').text() ;
			var bucket_description = data_row.children('.description').text() ;
			var bucket_is_pub = data_row.children('.is_pub').text() ;
			target.html('<input type="text" value="'+ old_value +'" id="edit_data" style="width:90%"/>') ;
			
			$('#edit_data').focus() ;
			$("#edit_data").keyup(function(e) {
				if (e.keyCode == 13) {
					new_value =  $("#edit_data").val() ;
					target.html(new_value) ;
					$.getJSON(api_endpoint+'/bucket/'+ bucket_secret +'/' + bucket_name + '?jsoncallback=?',
					{
						"method": 'post',
						"description":  data_row.children('.description').text(),
						"is_public": data_row.children('.is_pub').text()
					}, 
					function(json) {
						data_row.children('.upd_date').html(json['upd_date']);
						data_row.children('.description').html(json['description']) ;
						data_row.children('.is_pub').html( (json['is_public']==true) ? 'Yes' : 'No') ;
						edit_mode = false ;
					} );
				}
			});
			$('#edit_data').blur( function() {
				target.html(old_value) ;
				edit_mode = false ;
			}) ;
		}

		$("#new_bucket_button").click(function(e) {
			e.preventDefault();
			$("#new_bucket_form").show() ;
			$('#new_bucket_name').focus();
			$("#new_bucket_save_button").click(function(e){
				$.getJSON(api_endpoint+'/bucket/'+secret+'?jsoncallback=?',
				{
					"method": 'post',
					"name": $("#new_bucket_name").val() ,
					"description":  $("#new_bucket_description").val(),
					"is_public":  $("#new_bucket_is_public").val()
				},
				function(json) {
					$("#new_bucket_form").hide();
					show_user_buckets() ;
				}
				);
			}) ;
			$("#new_bucket_cancel_button").click(function(e){
				$('#new_bucket_name').val('');
				$('#new_bucket_description').val('');
				$('#new_bucket_is_public').val('No');
				$("#new_bucket_form").hide();
			}) ;
		}) ;
		
		$('.delete_bucket').click(function(e){
			var data_row = $(e.currentTarget).parents('tr') ;
			var bucket_name = data_row.children('.name').text() ;
			var ok = confirm('You are about to delete bucket "'+ bucket_name + '"');
			if (ok) {
				$.getJSON(api_endpoint+'/bucket/'+secret+'/'+bucket_name + '?jsoncallback=?',
				{"method": 'delete'}, 
				function(json) {
					data_row.remove() ;
				} );	
			}
		});
	});
}

