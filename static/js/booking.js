function init(){
    //會員系統
    menberSys();
    deleteCurrentBooking();
    returnHome();
    setUpSDK();
}
//當前使用者姓名
let myUser = null;
//會員系統函式
function menberSys(){
    //(流程1)檢查使用者狀況
    let signing = document.getElementById("signing");
    let nav = document.getElementById("nav");
    let userStatusUrl = "/api/user/status/";
    fetch(userStatusUrl).then((res)=>res.json())
    .then((jsonData)=>{
        if(jsonData["ok"] == true){
            myUser = jsonData["data"]["name"];
            signing.remove();
            let newSigning = document.createElement("p");
            newSigning.id = "sign_out";
            newSigning.className = "item";
            newSigning.textContent = "登出系統";
            nav.append(newSigning);
            //登入狀態才能查看訂單
            getBookingData();

            //(登出)
            let signOutUrl = "/api/user/signout/";
            let signout = document.getElementById("sign_out");
            signout.addEventListener("click",()=>{
                fetch(signOutUrl,{method:"DELETE",headers:{"Content-Type":"application/json"}})
                .then((res)=>res.json()).then((user)=>{
                    signout.remove();
                    signing = document.createElement("p");
                    signing.id = "signing";
                    signing.className = "item";
                    signing.textContent = "登入/註冊"
                    nav.append(signing);
                    window.setTimeout(()=>{
                        location.reload()
                    },600);
                });
            });
        }else{
            //如果使用者為登出狀態直接導回首頁
            window.setTimeout(()=>{
                location.href="/";
            },100);
        }
    });
    //(流程2)使者點擊彈出登入視窗
    let popupSignin = document.querySelector(".popup_form");
    let mask = document.querySelector(".mask");
    let signinCancle = document.querySelector(".cancle");
    signing.addEventListener("click",()=>{
        popupSignin.style.display = "block";
        mask.style.display = "block";
        cancleBox(signinCancle,popupSignin);
    });
    //(流程3)使用者完成登入步驟
    let signinForm = document.getElementById("signin_form");
    let signinResult = document.getElementById("signin_result");
    let signinUrl = "/api/user/signin/";
    signinForm.addEventListener("submit",(e)=>{
        e.preventDefault();
        let email = document.getElementById("signin_email").value;
        let password = document.getElementById("signin_pw").value;
        let data = {
            "email":email,
            "password":password
        };
        fetch(signinUrl,{method:"PATCH",headers:{"Content-Type":"application/json"}
        ,body:JSON.stringify(data)}).then((res)=>res.json())
        .then((user)=>{
            let ok = user["ok"];
            if(ok != null){
                signinResult.innerHTML = "登入成功!!";
                window.setTimeout(()=>{
                    location.reload()
                },1000);
            }else{
                let message = user["message"];
                signinResult.innerHTML = message;
            }
        });
    });
    //(流程4)使用者尚未註冊
    let popupSignup = document.querySelector(".popup_signup_form");
    let signupCancle = document.getElementById("signup_cancle");
    signinResult.addEventListener("click",()=>{
        popupSignin.style.display = "none";
        popupSignup.style.display = "block";
        cancleBox(signupCancle,popupSignup);
    });
    //(流程5)使用者完成註冊
    let signupForm = document.getElementById("signup_form");
    let signupResult = document.getElementById("signup_result");
    let signupUrl = "/api/user/signup/";
    signupForm.addEventListener("submit",(e)=>{
        e.preventDefault();
        let name = document.getElementById("signup_name").value;
        let email = document.getElementById("signup_email").value;
        let password = document.getElementById("signup_password").value;
        let data = {
            "name":name,
            "email":email,
            "password":password
        }
        fetch(signupUrl,{method:"POST",headers:{"Content-Type":"application/json"}
        ,body:JSON.stringify(data)}).then((res)=>res.json()).then((user)=>{
            let ok = user["ok"];
            if(ok != null){
                signupResult.innerHTML = "註冊成功!!";
            }else{
                let message = user["message"];
                signupResult.innerHTML = message;
            }
        });
    });
    //(流程6)使用者返回登入視窗
    signupResult.addEventListener("click",()=>{
        popupSignup.style.display = "none";
        popupSignin.style.display = "block";
    });
    //離開登入及註冊視窗函式
    function cancleBox(p1,p2){
        p1.addEventListener("click",()=>{
            p2.style.display = "none";
            mask.style.display = "none";
        });
    }
}
//取得使用者購物車預定資料
let amountPrice = null; //參數記錄使用者付款價格
let attractionDict = {} //記錄使用者行程資料供付款時確認資料
function getBookingData(){
    let bookDataUrl = "/api/booking/cart";
    fetch(bookDataUrl).then((res)=>res.json()).then((bookData)=>{
        if(bookData["ok"] == true){
            let loadImg = document.querySelector(".load_spot");
            loadImg.style.display = "none";
        }
        //使用者已登入會員
        if(bookData["error"] != true){
            if(bookData["message"] != "empty"){
                //景點id
                attractionDict["id"] = bookData["attraction"]["id"];
                //使用者名稱
                let username = document.getElementById("username");
                username.innerHTML = bookData["username"];
                //景點圖片
                let image = document.getElementById("slide_img");
                image.src = bookData["attraction"]["image"];
                attractionDict["image"] = bookData["attraction"]["image"];
                //景點名稱
                let spotname = document.getElementById("spotname");
                spotname.innerHTML = bookData["attraction"]["name"];
                attractionDict["name"] = bookData["attraction"]["name"];
                //預定日期
                let date = document.getElementById("date");
                date.innerHTML = bookData["date"];
                attractionDict["date"] = bookData["date"];
                //預定時間
                let showtime = document.getElementById("time");
                let time = bookData["time"];
                if(time == "morning"){
                    showtime.innerHTML = "早上9點到下午4點";
                    attractionDict["time"] = "morning";
                }else{
                    showtime.innerHTML = "下午2點到晚上9點";
                    attractionDict["time"] = "afternoon";
                };
                //預定費用
                let price = document.getElementById("price");
                price.innerHTML = "新台幣"+bookData["price"]+"元";
                attractionDict["price"] = bookData["price"]; 
                //景點地址
                let address = document.getElementById("place");
                address.innerHTML = bookData["attraction"]["address"];
                attractionDict["address"] = bookData["attraction"]["address"];
                //確認付款
                let totalPrice = document.getElementById("total_price");
                totalPrice.innerHTML = bookData["price"];
            }else{
                let loadImg = document.querySelector(".load_spot");
                loadImg.style.display = "none";

                let container = document.querySelector(".container");
                container.style.display = "none";
                let hr2 = document.querySelector(".hr2");
                hr2.style.display = "none";
                let contactMessage = document.querySelector(".contact_message");
                contactMessage.style.display = "none";
                let hr3 = document.querySelector(".hr3");
                hr3.style.display = "none";
                let paidMessage = document.querySelector(".paid_message");
                paidMessage.style.display = "none";
                let hr4 = document.querySelector(".hr4");
                hr4.style.display = "none";
                let confirm = document.querySelector(".confirm");
                confirm.style.display = "none";
                //使用者名稱
                let username = document.getElementById("username");
                username.innerHTML = bookData["username"];
                let noData = document.getElementById("nodata");
                noData.style.display = "block";
                let footer = document.getElementById("footer");
                footer.style.height = "576px";
            }
        //使用者未登入
        }else{
            let message = bookData["message"];
        }
    });
}
//刪除已預定的行程
function deleteCurrentBooking(){
    let deleteBooking = document.querySelector(".delete_booking");
    let deleteBookingUrl = "/api/booking/cancle";
    deleteBooking.addEventListener("click",()=>{
        fetch(deleteBookingUrl,{method:"DELETE",headers:{"Content-Type":"application/json"}})
        .then((res)=>res.json()).then((bookStatus)=>{
            console.log(bookStatus);
            window.setTimeout(()=>{
                location.reload();
            },100);
        });
    });
}
//點擊台北一日遊回到首頁
function returnHome(){
    let home = document.getElementById("backto_home");
    home.addEventListener("click",()=>{
        location.href = "/";
    });
}
//TapPay setupSDK
function setUpSDK(){
    TPDirect.setupSDK(20437,"app_3xNskPzPUaYioKPxBq1wN5on3otD9ZavOSh1N3yFG6MU3PuHvqIAylKwzeIi",'sandbox');
    // Display ccv field
    let fields = {
        number: {
            // css selector
            element: '#card-number',
            placeholder: '**** **** **** ****'
        },
        expirationDate: {
            // DOM object
            element: document.getElementById('card-expiration-date'),
            placeholder: 'MM / YY'
        },
        ccv: {
            element: '#card-ccv',
            placeholder: 'ccv'
        }
    };
    TPDirect.card.setup({
        fields: fields,
        styles: {
            'input': {
                'color': 'gray'
            },
            // style valid state
            '.valid': {
                'color': 'green'
            },
            // style invalid state
            '.invalid': {
                'color': 'red'
            },
            // Media queries
            // Note that these apply to the iframe, not the root window.
            '@media screen and (max-width: 400px)': {
                'input': {
                    'color': 'orange'
                }
            }
        }
    });
}
function onClick(){
    let name = document.getElementById("contact-name").value;
    let email = document.getElementById("contact-email").value;
    let phone = document.getElementById("contact-phone").value;
    TPDirect.card.getPrime((result)=>{
        if(result.status !== 0){
            return
        }
        let prime = result.card.prime;
        //將資料傳入後端
        let post_data = {
            "prime":prime,
            "order":{
                "price":attractionDict["price"],
                "trip":{
                    "attraction":{
                        "id":attractionDict["id"],
                        "name":attractionDict["name"],
                        "address":attractionDict["address"],
                        "image":attractionDict["image"]
                    },
                    "date":attractionDict["date"],
                    "time":attractionDict["time"]
                },
                "contact":{
                    "name":name,
                    "email":email,
                    "phone":phone
                }
            }
        }
        let ordersUrl = "/api/orders";
        fetch(ordersUrl,{method:"POST",headers:{"Content-Type":"application/json"}
        ,body:JSON.stringify(post_data)})
        .then((res)=>res.json()).then((jsonData)=>{
            let error = jsonData["error"];
            let message = jsonData["message"];
            if(error!=true){
                let number = jsonData["data"]["number"];
                //將編號傳至api/order/
                //付款成功後將使用者導至感謝頁面
                window.setTimeout(()=>{
                    location.href = "/thankyou?number="+number;
                },100);
            }else if(message == "未正確填寫資料"){
                alert(message);
            }
        });
    });
};