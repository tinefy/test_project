let vm = new Vue(
    {
        el: '#app',
        delimiters: ['[[', ']]'],
        data: {
            // username: getCookie('username'),
            username: username,
            password: '',
            new_password: '',
            new_password2: '',
            error_password: false,
            error_new_password: false,
            error_new_password2: false,
            tip: '',
        },
        methods: {
            clear_error: function () {
                this.error_password = false;
                this.error_new_password = false;
                this.error_new_password2 = false;
            },
            clear_form: function (tip=true) {
                this.password = '';
                this.new_password = '';
                this.new_password2 = '';
                this.clear_error();
                if (tip) {
                    this.tip = '';
                }
            },
            check_password: function (password = 'old') {
                let re = /^[\w\d]{8,20}$/;
                if (password === 'old') {
                    if (re.test(this.password)) {
                        this.error_password = false;
                    } else {
                        this.error_password = true;
                    }
                } else if (password === 'new') {
                    if (re.test(this.new_password)) {
                        this.error_new_password = false;
                    } else {
                        this.error_new_password = true;
                    }
                } else if (password === 'new2') {
                    if (this.new_password2 === this.new_password) {
                        this.error_new_password2 = false;
                    } else {
                        this.error_new_password2 = true;
                    }
                }
            },
            save_new_password: function () {
                this.check_password()
                this.check_password('new')
                this.check_password('new2')
                if (this.error_password === false && this.error_new_password === false && this.error_new_password2 === false) {
                    let url = '/info/password/';
                    let data_ = {
                        old_password: this.password,
                        new_password: this.new_password,
                        new_password2: this.new_password2,
                    };
                    axios.put(
                        url, data_, {
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            responseType: 'json',
                        }
                    ).then(
                        response => {
                            this.tip = response.data.errmsg;
                            this.clear_form(false);
                        }
                    ).catch(
                        error => {
                            console.log(error.response);
                        }
                    )
                }
            },
            cancel_new_password: function () {
                this.clear_form();
            },

        },
    }
)