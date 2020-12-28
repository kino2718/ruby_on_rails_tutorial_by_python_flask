(function() {
	function get_csrf_param() {
		// meta tag で属性 name、 値 "csrf-token" を含む要素を取得する。
		var el = document.querySelector('meta[name=csrf-param]');
		// 要素が存在したら属性 content の値を返す。
		return el && el.content;
	}

	function get_csrf_token() {
		// meta tag で属性 name、 値 "csrf-token" を含む要素を取得する。
		var el = document.querySelector('meta[name=csrf-token]');
		return el && el.content;
	}

	function get_links_with_data_method() {
		// link tag で属性 data-method を含む要素を取得する。
		var atags = document.getElementsByTagName('a');
		var els = [];
		for (var i = 0; i < atags.length; i++) {
			var el = atags[i];
			if (el.hasAttribute('data-method')) {
				els.push(el);
			}
		}
		return els;
	}

	csrf_param = get_csrf_param();
	csrf_token = get_csrf_token();
	links_with_data_method = get_links_with_data_method();

	// data-method属性を持つ link tag にPOST動作をさせる
	for (var i = 0; i < links_with_data_method.length; i++) {
		var link = links_with_data_method[i];
		var method = link.getAttribute('data-method');
		link.onclick = function(e) {
			// form要素を作成
			var form = document.createElement('form');
			var form_content = "<input name='_method' value='" + method +
			"' type='hiden' />";
			form_content += "<input name='" + csrf_param +
			"' value='" + csrf_token + "' type='hiden' />";
			form_content += '<input type="submit" />';
			// methodをPOSTにする
			form.method = 'post';
			form.action = link.href;
			form.target = link.target;
			form.innerHTML = form_content;
			form.style.display = 'none';
			document.body.appendChild(form);
			// 送信
			form.querySelector('[type="submit"]').click();
			return false; // link の GET 動作を disable にする
		};
	}
})();
