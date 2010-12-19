api_endpoint = '/api' ;

function show_bucket_contents(bucket_name, secret) {
	var url = api_endpoint+'/bucket/'+secret+'/'+bucket_name+'/item?jsoncallback=?' ;
	$.getJSON(url, function(items){
		$("#data").html('');
		
		var html = '' ;
		html = html + '<h2>'+bucket_name+' items</h2>\n' ;
		html = html + '<table id="items_table" class="bucket"></table>' ;
		$("#data").append(html) ;
		
		var html = '' ;
		html = html + '<tr><th>application</th><th>datatype</th><th>name</th><th>content</th>' ;
		html = html + '<th>updated</th>' ;
		html = html + '<th class="actions"><input type="button" id="new_item_button" value="new"/></tr>' ;
		$('#items_table').append(html) ;
		
		html = '<tr id="new_item_form">' ;
		html = html + '<td><input type="text" id="new_item_application" style="width:100%" /></td>';
		html = html + '<td><input type="text" id="new_item_datatype" style="width:100%" /></td>';
		html = html + '<td><input type="text" id="new_item_name"/ style="width:100%" ></td>' ;
		html = html + '<td><input type="text" id="new_item_content" style="width:100%" /></td>';
		html = html + '<td colspan="3"></td>';
		html = html + '<td class="actions"><input type="button" id="new_item_save_button" value="save" /> <input type="button" id="new_item_cancel_button" value="cancel" /></td>\n';
		html = html + '</tr>\n' ;
		$('#items_table').append(html) ;

		for(var i=0,len=items.length; item=items[i],i<len; i++){
			html = '<tr class="row">' ;
			html = html + '<td class="application">'+item['application']+'</td>' ;
			html = html + '<td class="datatype">'+item['datatype']+'</td>' ;
			html = html + '<td class="name">'+item['name']+'</td>';
			html = html + '<td class="content"><div>'+item['content']+'&nbsp;</div></td>' ;
			// html = html + '<td class="date cre_date">'+item['cre_date'].substr(0,19)+'</td>' ;
			html = html + '<td class="date upd_date">'+item['upd_date'].substr(0,19)+'</td>' ;
			// html = html + '<td class="date exp_date">'+item['exp_date']+'</td>' ;
			html = html + '<td class="actions">';
			html = html + '<a href="#" class="button delete_item">x</a></td></tr>' ;
			
			$('#items_table').append(html);
		}
		edit_mode = false ;
		
		$("#items_table").delegate(".datatype", "click", function(e){
			if (!edit_mode) edit_item(e);
		});
		
		$("#items_table").delegate(".application", "click", function(e){
			if (!edit_mode) edit_item(e);
		});
		
		$("#items_table").delegate(".content>div", "click", function(e){
			if (!edit_mode) edit_item(e);
		});
		
		function edit_item(e){
			var target = $(e.currentTarget);
			var old_value = target.html();
			edit_mode = true ;
			var data_row = target.parents('tr') ;
			var item_name = data_row.children('.name').text() ;
			var item_application = data_row.children('.application').text() ;
			var item_content = data_row.children('.content>div').text() ;
			target.html('<input type="text" value="'+ old_value +'" id="edit_data" style="width:90%"/>') ;
			
			$('#edit_data').focus() ;
			$("#edit_data").keyup(function(e) {
				if (e.keyCode == 13) {
					new_value =  $("#edit_data").val() ;
					target.html(new_value) ;
					$.ajax({
						type: "POST",
						url: api_endpoint+'/bucket/'+ secret +'/' + bucket_name + '/item/'+ item_name,
						data: {
							"content":  data_row.children('.content').text(),
							"application":  data_row.children('.application').text(),
							"datatype":  data_row.children('.datatype').text()
						},
						success: function(data){
							json = $.parseJSON(data) ;
							data_row.children('.application').html(json['application']) ;
							data_row.children('.content>div').html(json['content']) ;
							data_row.children('.datatype').html(json['datatype']) ;
							edit_mode = false ;
						}
					});
				}
			});
			$('#edit_data').blur( function() {
				target.html(old_value) ;
				edit_mode = false ;
			}) ;
		}

		$("#new_item_button").click(function(e) {
			e.preventDefault();
			$("#new_item_form").show() ;
			$('#new_item_name').focus();
			$("#new_item_save_button").click(function(e){
				$.ajax({
					type: "POST",
					url: api_endpoint+'/bucket/'+secret+'/'+bucket_name+'/item',
					data: {
						"name": $("#new_item_name").val() ,
						"application":  $("#new_item_application").val(),
						"datatype":  $("#new_item_datatype").val(),
						"content":  $("#new_item_content").val()
					},
					success: function(data) {
						item = $.parseJSON(data) ;
						html = '' ;
						html = html + '<tr class="row"><td class="name">'+item['name']+'</td>';
						html = html + '<td class="application">'+item['application']+'</td>' ;
						html = html + '<td class="datatype">'+item['datatype']+'</td>' ;
						html = html + '<td class="content">'+item['content']+'</td>' ;
						html = html + '<td class="date cre_date">'+item['cre_date'].substr(0,19)+'</td>' ;
						html = html + '<td class="date upd_date">'+item['upd_date'].substr(0,19)+'</td>' ;
						html = html + '<td class="date exp_date">'+item['exp_date']+'</td>' ;
						html = html + '<td class="actions">';
						html = html + '<a href="#" class="button delete_item">x</a></td></tr>' ;
						$('#items_table').append(html);
						$("#new_item_form").hide();
					}
				});
			}) ;
			
			$("#new_item_cancel_button").click(function(e){
				$('#new_item_name').val('');
				$('#new_item_application').val('');
				$('#new_item_content').val('');
				$("#new_item_form").hide();
			}) ;
		}) ;
		
		$('.delete_item').click(function(e){
			var data_row = $(e.currentTarget).parents('tr') ;
			var item_name = data_row.children('.name').text() ;
			var ok = confirm('You are about to delete item "'+ item_name + '"');
			if (ok) {
				$.getJSON(api_endpoint+'/bucket/'+secret+'/'+bucket_name + '/item/' + item_name + '?jsoncallback=?',
				{"method": 'delete'}, 
				function(json) {
					data_row.remove() ;
				} );	
			}
		});
	});
}

