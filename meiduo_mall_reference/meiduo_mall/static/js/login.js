let vm = new Vue(
    {
        el: '#app',
        delimiters: ['[[', ']]'],
        data: {
            username: '',
            password: '',
            remembered: '',

            err_username: false,
            err_password: false,
        },
        methods: {
            check_username: function () {
                let re = /^[\w\d_-]{5,20}$/;
                if (re.test(this.username)) {
                    this.err_username = false;
                } else {
                    this.err_username = true;
                }
            },
            check_password: function () {
                let re = /^[\w\d]{8,20}$/;
                if (re.test(this.password)) {
                    this.err_password = false;
                } else {
                    this.err_password = true;
                }
            },
            on_submit: function (event) {
                this.check_username();
                this.check_password();
                if (this.err_username || this.err_password) {
                    event.preventDefault()
                }
            },
            github_login: function (event) {
                event.preventDefault();
                let next = get_query_string('next') || '/';
                let url = '/github/login/?next=' + next;
                axios.get(
                    url,{responseType:'json'}
                ).then(
                    response=>{
                        location.href=response.data.login_url;
                    }
                ).catch(
                    error=>{
                        console.log(error.response)
                    }
                )
            },
        },
    }
)