function init(){
    returnHome();
    getData();
    menberSys();
}
function returnHome(){
    let title = document.getElementById("backto_home");
    title.addEventListener("click",()=>{
        location.href = "/";
    });
}
function getorderNumber(){
    let url = location.href;
    let urlParam = new URL(url);
    let number = urlParam.searchParams.get("number");
    return number;
}
function getData(){
    let number = getorderNumber();
    url = "/api/order/"+number;
    fetch(url).then((res)=>res.json()).then((result)=>{
        let error = result["error"];
        if(error != true){
            let num = document.getElementById("order_num");
            num.innerHTML = result["data"]["number"];
            let paidresult = document.getElementById("order_paid");
            if(result["data"]["status"] == "已付款"){
                paidresult.innerHTML = "付款成功!!";
                //付款成功後將資料庫預定資料移除以免使用者重複付款
                let deleteBookingdataUrl = "/api/booking/cancle" ;
                fetch(deleteBookingdataUrl,{method:"DELETE",headers:{"Content-Type":"application/json"}})
                .then((res)=>res.json()).then((result)=>{
                    let ok = result["ok"];
                    if(ok == true){
                        let signoutbtn = document.getElementById("sign_out");
                        signoutbtn.addEventListener("click",()=>{
                            window.setTimeout(()=>{
                                location.href = "/";
                            },100);
                        }); 
                    }else{
                        window.setTimeout(()=>{
                            location.href = "/";
                        },100);
                    }
                });
            }else{
                paidresult.innerHTML = "付款失敗!!";
            }
        }else{
            location.href = "/";
        }
    });
}
//會員系統函式
function menberSys(){
    //(流程1)檢查使用者狀況
    let signing = document.getElementById("signing");
    let nav = document.getElementById("nav");
    let userStatusUrl = "/api/user/status/";
    fetch(userStatusUrl).then((res)=>res.json())
    .then((jsonData)=>{
        if(jsonData != null){
            myUser = jsonData["data"]["name"];
            signing.remove();
            let newSigning = document.createElement("p");
            newSigning.id = "sign_out";
            newSigning.className = "item";
            newSigning.textContent = "登出系統";
            nav.append(newSigning);

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
                        location.reload();
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