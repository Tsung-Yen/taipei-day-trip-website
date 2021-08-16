function init(){
    connect();
    menberSys();
    bookSchedule();
    bookingCart();
    returnHome();
}
//會員系統
function menberSys(){
    //偵測使用者狀態
    let sign = document.getElementById("sign");
    let statusUrl = "/api/user/status/";
    let nav = document.getElementById("nav");
    fetch(statusUrl).then((res=>res.json()))
    .then((user)=>{
        if(user["ok"] == true){
            //使用者已登入系統
            sign.remove();
            let newSign = document.createElement("p");
            newSign.className = "item";
            newSign.id = "sign_out";
            newSign.textContent = "登出系統";
            nav.append(newSign);
            //(使用者登出，透過method將key清空)
            let signOut = document.getElementById("sign_out");
            signOut.addEventListener("click",()=>{
                let signOutUrl = "/api/user/signout/";
                fetch(signOutUrl,{method:"DELETE"},headers={"Content-Type":"application/json"});
                signOut.remove();
                sign = document.createElement("p");
                sign.className = "item";
                sign.id = "sign";
                sign.textContent = "登入/註冊";
                nav.append(sign);
                window.setTimeout(()=>{
                    location.reload();
                },300);
            });
        }
    });
    //(操作1:使用者點擊彈出登入視窗)
    let popupForm = document.querySelector(".popup_form");
    let mask = document.querySelector(".mask");
    let signinCancle = document.querySelector(".cancle");
    sign.addEventListener("click",()=>{
        popupForm.style.display = "block";
        mask.style.display = "block";
        cancleBox(signinCancle,popupForm);
    });
    //(操作2:使用者登入)
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
            if(ok == true){
                signinResult.innerHTML = "登入成功!!";
                window.setTimeout(()=>{
                    location.reload();
                },1000);
            }else{
                let message = user["message"];
                signinResult.innerHTML = message;
            }
        });
    });
    //(操作3:使用者尚未註冊)
    let popupSignupForm = document.querySelector(".popup_signup_form");
    let signupCancle = document.getElementById("signup_cancle");
    signinResult.addEventListener("click",()=>{
        popupForm.style.display = "none";
        popupSignupForm.style.display = "block";
        cancleBox(signupCancle,popupSignupForm);
    });
    //(操作4:使用者完成註冊)
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
        };
        fetch(signupUrl,{method:"POST",headers:{"Content-Type":"application/json"}
        ,body:JSON.stringify(data)}).then((res)=>res.json())
        .then((user)=>{
            let ok = user["ok"];
            if(ok == true){
                signupResult.innerHTML = "註冊成功!!點此返回登入頁面";
            }else{
                let message = user["message"];
                signupResult.innerHTML = message;
            }
        });
    });
    //(操作5:使用者返回登入)
    signupResult.addEventListener("click",()=>{
        popupSignupForm.style.display = "none";
        popupForm.style.display = "block";
    });

    //(返回按鈕)
    function cancleBox(p1,p2){
        p1.addEventListener("click" , function(){
            p2.style.display = "none";
            mask.style.display = "none";
        });
    }
}
//開始預定(attraction頁面，建立新的預定系統)
function bookSchedule(){
    let morning = document.querySelector(".radio1");
    let afternoon = document.querySelector(".radio2");
    let time = null;
    let price = null;
    //取得使用者當前資料序號
    let attractionId = pathData;
    //使用者選擇早上
    morning.addEventListener("click",()=>{
        time = "morning";
        price = 2000;
    });
    //使用者選擇下午
    afternoon.addEventListener("click",()=>{
        time = "afternoon";
        price = 2500
    });
    let bookForm = document.getElementById("book_form");
    bookForm.addEventListener("submit",(e)=>{
        e.preventDefault();
        let date = document.querySelector(".inputdate").value;
        let data = {
            "attractionId":attractionId,
            "date":date,
            "time":time,
            "price":price
        }
        //將使用者選擇預定時間地點資料傳給後端
        let newBookingUrl = "/api/booking/schedule";
        fetch(newBookingUrl,{method:"POST",headers:{"Content-Type":"application/json"}
        ,body:JSON.stringify(data)}).then((res)=>res.json()).then((result)=>{
            let ok = result["ok"];
            if(ok == true){
                console.log(result);
                window.setTimeout(()=>{
                    location.href = "/booking";
                },200);
            }else{
                let message = result["message"];
                if(message == "未登入"){
                    //使用者尚未登入，登入視窗彈出
                    let popupForm = document.querySelector(".popup_form");
                    let mask = document.querySelector(".mask");
                    let signinCancle = document.querySelector(".cancle");
                    popupForm.style.display = "block";
                    mask.style.display = "block";
                    cancleBox(signinCancle,popupForm,mask);
                }else{
                    //輸入日期已過
                    let message = result["message"];
                    alert(message);
                }
            }
        });
    });
    //(離開登入頁面)
    function cancleBox(p1,p2,p3){
        p1.addEventListener("click" , function(){
            p2.style.display = "none";
            p3.style.display = "none";
        });
    }
}
//查看預定完成後的購物車(使用者點擊預定行程，單純點擊跳轉程序)
function bookingCart(){
    let booking = document.getElementById("booking");
    let statusUrl = "/api/user/status/";
    booking.addEventListener("click",()=>{
        //先檢查使用者狀態(如果尚未登入直接倒回首頁，已登入可進入購物車頁面)
        fetch(statusUrl).then((res)=>res.json()).then((user)=>{
            if(user["ok"]==true){
                location.href = "/booking";
            }else{
                //使用者尚未登入，登入視窗彈出
                let popupForm = document.querySelector(".popup_form");
                let mask = document.querySelector(".mask");
                let signinCancle = document.querySelector(".cancle");
                popupForm.style.display = "block";
                mask.style.display = "block";
                cancleBox(signinCancle,popupForm,mask);
            }
        });
    });

    //(返回按鈕)
    function cancleBox(p1,p2,p3){
        p1.addEventListener("click" , function(){
            p2.style.display = "none";
            p3.style.display = "none";
        });
    }
}
//點擊台北一日遊回到首頁
function returnHome(){
    let home = document.getElementById("backto_home");
    home.addEventListener("click",()=>{
        location.href = "/";
    });
}
//connecting to Ajax
var path = window.location.href;
var data = path.split("/");
var pathData = data[4];
function connect(){
    url = "/api/attraction/"+pathData;
    fetch(url).then(res=>res.json())
    .then((jsondata)=>{
        if(jsondata!=null){
            let loadImg = document.querySelector(".load_spot");
            loadImg.style.display = "none";
        }
        //以下為此路由邏輯
        let name = jsondata['name'];
        let category = jsondata['category'];
        let mrt = jsondata['mrt'];
        let description = jsondata['description'];
        let address = jsondata['address'];
        let transport = jsondata['transport'];
        let imageData = jsondata['images'];
        let image = imageData.slice(0,-1);
        let images = image[0];
        //圖片更換(上半部:圖片輪播及購票資訊)
        let slideimg = document.querySelector(".slideimg");
        let img = document.createElement("img");
        img.src = images;
        img.id = "showImg";
        slideimg.append(img);
        let bookingcont = document.querySelector(".bookingContent");
        let spotname = document.querySelector(".spotname");
        spotname.textContent = name;
        let catmrt = document.querySelector(".catmrt");
        catmrt.textContent = category+" at "+mrt;


        //下半部(description,address,transport)
        let content = document.querySelector(".content");
        let descrip = document.createElement("div");
        descrip.textContent = description;
        descrip.className = "description";
        content.append(descrip);
        //address
        let adds = document.createElement("div");
        adds.className = "address";
        let addt = document.createElement("p");
        addt.textContent = "景點地址 : ";
        addt.className = "addt";
        let addcont = document.createElement("p");
        addcont.textContent = address;
        content.append(adds);
        adds.append(addt);
        adds.append(addcont);
        //transport
        let trans = document.createElement("div");
        trans.className = "transport";
        let transt = document.createElement("p");
        transt.textContent = "交通方式 : ";
        transt.className = "transt";
        let transcont = document.createElement("p");
        transcont.textContent = transport;
        content.append(trans);
        trans.append(transt);
        trans.append(transcont);

        //get user select time
        let dot1 = document.querySelector(".radio1");
        let fee = document.querySelector(".p3");
        dot1.addEventListener("click" , function(){
            fee.innerHTML = "新台幣2000元";
        })
        let dot2 = document.querySelector(".radio2");
        dot2.addEventListener("click" , function(){
            fee.innerHTML = "新台幣2500元";
        })
    
        //change img & img location dot
        //圖片順序位置
        let dotLocation = document.querySelector(".img_dot");
        let imgdotNum = image.length;
        let borde = 0;
        for(let i=0;i<imgdotNum;i++){
            let circle = document.createElement("div");
            circle.className = "circle";
            circle.id = "circle"+i;
            dotLocation.append(circle);
            document.getElementById("circle"+i).style.flex = "none";
            if(i == 0){
                document.getElementById("circle"+i).style.marginLeft = borde+"px";
            }else if(i > 0){
                borde=10;
                document.getElementById("circle"+i).style.marginLeft = borde+"px";
            }else if(i == imgdotNum-1){
                borde=10;
                document.getElementById("circle"+i).style.marginLeft = borde+"px";
            }
        };
        //#按鈕切換圖片
        //網頁載入顯示第一張
        let curDot = document.getElementById("circle0");
        curDot.style.backgroundColor = "rgb(128, 118, 118)";

        let currentImgNum = 0;
        let lastImg = null;
        let next = document.querySelector(".right");
        let prev = document.querySelector(".left");
        let curImg = document.getElementById("showImg");
        next.addEventListener("click" , function(){
            if(currentImgNum == 0){
                currentImgNum++;
            }else if(currentImgNum < image.length-1){
                currentImgNum++;
            }else{
                lastImg = currentImgNum;
                currentImgNum = 0
            }
            curImg.src = image[currentImgNum];
            //圖片位置處理
            if(currentImgNum > 0){
                //如果目前圖片index大於零，將圖片變為黑色
                let curDot0 = document.getElementById("circle"+currentImgNum);
                curDot0.style.backgroundColor = "rgb(128, 118, 118)";
                //使用迴圈找出所有不是當前圖片編號的圓點，並將其變成白色
                for(let i =0;i<currentImgNum;i++){
                    if(currentImgNum!=i){
                        let curDot = document.getElementById("circle"+i);
                        curDot.style.backgroundColor = "white";
                    }
                }
            }else if(currentImgNum == 0){
                //如果圖片等於0將停在最後的黑點變白
                let curDot = document.getElementById("circle0");
                curDot.style.backgroundColor = "rgb(128, 118, 118)";
                document.getElementById("circle"+lastImg).style.backgroundColor = "white";
            }
        });

        //Auto change Image
        window.setInterval(()=>{
            if(currentImgNum < image.length-1){
                currentImgNum++;
            }else{
                lastImg = currentImgNum;
                currentImgNum = 0
            }
            curImg.src = image[currentImgNum];
            if(currentImgNum > 0){
                let curDot0 = document.getElementById("circle"+currentImgNum);
                curDot0.style.backgroundColor = "rgb(128, 118, 118)";
                for(let i =0;i<currentImgNum;i++){
                    if(currentImgNum!=i){
                        let curDot = document.getElementById("circle"+i);
                        curDot.style.backgroundColor = "white";
                    }
                }
            }else if(currentImgNum == 0){
                //如果圖片等於0將停在最後的黑點變白
                let curDot = document.getElementById("circle0");
                curDot.style.backgroundColor = "rgb(128, 118, 118)";
                document.getElementById("circle"+lastImg).style.backgroundColor = "white";
            }
            
        },1500); 

        prev.addEventListener("click" , function(){
            if(currentImgNum == 0){
                currentImgNum = image.length-1;
            }else if(currentImgNum < image.lenght-1 || currentImgNum !=0){
                currentImgNum = currentImgNum-1;
            }else if(currentImgNum == image.length-1){
                currentImgNum = currentImgNum-1;
            }
            curImg.src = image[currentImgNum];
            //圖片位置處理
            if(currentImgNum > 0){
                let curDot0 = document.getElementById("circle"+currentImgNum);
                curDot0.style.backgroundColor = "rgb(128, 118, 118)";
                document.getElementById("circle0").style.backgroundColor = "white";
                //使用迴圈找出所有不是當前圖片編號的圓點，並將其變成白色
                for(let i =0;i<image.length;i++){
                    if(currentImgNum!=i){
                        let curDot = document.getElementById("circle"+i);
                        curDot.style.backgroundColor = "white";
                    }
                }
            }else if(currentImgNum == 0){
                let curDot = document.getElementById("circle0");
                curDot.style.backgroundColor = "rgb(128, 118, 118)";
                document.getElementById("circle1").style.backgroundColor = "white";
            }
        });
    });
}