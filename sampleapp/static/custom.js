(function() {
    function get_csrf_param() {
        // meta tag で属性 name、 値 "csrf-token" を含む要素を取得する。
        let el = document.querySelector('meta[name=csrf-param]');
        // 要素が存在したら属性 content の値を返す。
        return el && el.content;
    }

    function get_csrf_token() {
        // meta tag で属性 name、 値 "csrf-token" を含む要素を取得する。
        let el = document.querySelector('meta[name=csrf-token]');
        return el && el.content;
    }

    function get_links_with_data_method() {
        // link tag で属性 data-method を含む要素を取得する。
        let atags = document.getElementsByTagName('a');
        let els = [];
        for (let i = 0; i < atags.length; i++) {
            let el = atags[i];
            if (el.hasAttribute('data-method')) {
                els.push(el);
            }
        }
        return els;
    }

    let csrf_param = get_csrf_param();
    let csrf_token = get_csrf_token();
    let links_with_data_method = get_links_with_data_method();

    // data-method属性を持つ link tag にPOST動作をさせる
    for (let i = 0; i < links_with_data_method.length; i++) {
        let link = links_with_data_method[i];
        link.onclick = function(e) {
            let method = link.getAttribute('data-method');
            // form要素を作成
            let form = document.createElement('form');
            let form_content =
            `<input name="_method" value="${method}" type="hiden" />
            <input name="${csrf_param}" value="${csrf_token}" type="hiden" />
            <input type="submit" />`;
            // methodをPOSTにする
            form.method = 'post';
            form.action = link.href;
            form.target = link.target;
            form.innerHTML = form_content;
            form.style.display = 'none';

            // data-confirm属性がある時は確認のダイアログを出す
            let message = link.getAttribute('data-confirm')
            if (message) {
                form.onsubmit = function(e) {
                    return window.confirm(message)
                }
            }

            document.body.appendChild(form);
            // 送信
            form.querySelector('[type="submit"]').click();
            return false; // link の GET 動作を disable にする
        };
    }

    // idがmicropost_imageの要素を見つけ出し、その要素で指定されるファイルサイズが
    // 5MB以上ならファイル添付を取り消す
    let element = document.getElementById('micropost_image');
    if (element) {
        element.onchange = function(e) {
            let size_in_megabytes = this.files[0].size/1024/1024;
            if (size_in_megabytes > 5) {
                alert("Maximum file size is 5MB. Please choose a smaller file.");
                this.value = '';
            }
        }
    }

    // Ajaxで非同期通信でユーザーのフォロー・アンフォローを行う。
    // RailsではJavaScriptのコードを受取り動的に実行しているが、ここでは
    // 単にJSONデータを受取りそれに基づいてhtmlを書き換えることにする。
    // JavaScriptは初心者なので取り敢えず動くレベルを目指す。
    function set_ajax() {
        let form = document.querySelector('form[data-remote="true"]');
        if (form == null) return;

        let button = form.querySelector('[type="submit"]');
        if (button == null) return;

        if (button.value == 'Follow') {
            button.onclick = function(e) {
                let xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function() {
                    if (xhr.readyState == 4) {
                        // レスポンス受信完了
                        if (xhr.status == 200) {
                            // 通信正常完了
                            let res = JSON.parse(xhr.responseText);
                            if (res.result == 'ok') {
                                document.querySelector('#followers').innerHTML =
                                    res.followers;
                                let html =
                                    `<form action="/relationships/${res.relation_id}"
                                    accept-charset="UTF-8"
                                    data-remote="true"
                                    method="post">
                                    <input type="hidden" name="_method"
                                    value="delete" />
                                    <input type="hidden"
                                    name="authenticity_token"
                                    value="${res.csrf_token}" />
                                    <input type="submit" name="commit"
                                    value="Unfollow" class="btn" />`;
                                document.querySelector('#follow_form').
                                    innerHTML = html;
                                set_ajax();
                            }
                        }
                    }
                }
                xhr.open('POST', form.action);
                xhr.setRequestHeader('Content-Type',
                                     'application/x-www-form-urlencoded');
                xhr.setRequestHeader('Accept','application/json');

                let body = 'authenticity_token=' +
                form.querySelector('input[name="authenticity_token"]').value +
                '&followed_id=' +
                form.querySelector('input[name="followed_id"]').value +
                '&commit=Follow';
                xhr.send(body);
                return false;
            }
        }
        else if (button.value == 'Unfollow') {
            button.onclick = function(e) {
                let xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function() {
                    if (xhr.readyState == 4) {
                        // レスポンス受信完了
                        if (xhr.status == 200) {
                            // 通信正常完了
                            res = JSON.parse(xhr.responseText);
                            if (res.result == 'ok') {
                                document.querySelector('#followers').innerHTML =
                                    res.followers;
                                html =
                                    `<form action="/relationships"
                                    accept-charset="UTF-8"
                                    data-remote="true" method="post">
                                    <input type="hidden"
                                    name="authenticity_token"
                                    value="${res.csrf_token}" />
                                    <input type="hidden" name="followed_id"
                                    id="followed_id" value="${res.user_id}" />
                                    <input type="submit" name="commit"
                                    value="Follow" class="btn btn-primary" />`;
                                document.querySelector('#follow_form').
                                    innerHTML = html;
                                set_ajax();
                            }
                        }
                    }
                }
                xhr.open('POST', form.action);
                xhr.setRequestHeader('Content-Type',
                                     'application/x-www-form-urlencoded');
                xhr.setRequestHeader('Accept','application/json');

                let body = 'authenticity_token=' +
                form.querySelector('input[name="authenticity_token"]').value +
                '&_method=' +
                form.querySelector('input[name="_method"]').value +
                '&commit=Unfollow';
                xhr.send(body);
                return false;
            }
        }
    }
    set_ajax();
})();
