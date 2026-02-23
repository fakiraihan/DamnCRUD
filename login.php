<?php
include "functions.php";
session_start();

$notif = null;
if (isset($_POST['username']) && isset($_POST['password'])) {
    $user = $_POST['username'];
    $pass = $_POST['password'];
    $salt = "XDrBmrW9g2fb";
    $pdo = pdo_connect();
    $hashed_pass = hash('sha256', $pass . $salt);
    $stmt = $pdo->prepare('SELECT * FROM users WHERE username = :username AND password = :password LIMIT 1');
    $stmt->execute([
        ':username' => $user,
        ':password' => $hashed_pass
    ]);
    if ($stmt->rowCount() > 0) {
        session_regenerate_id(true);
        $_SESSION['user'] = $user;
        header("location: index.php");
        exit;
    } else {
        $notif = "Damn, wrong credentials!!";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <?= style_script() ?>
    <title>Login</title>
</head>
<body class="text-center">
    <form class="form-signin" method="POST">
        <h1 class="h3 mb-3 font-weight-normal">Damn, sign in!</h1>
        <label for="inputUsername" class="sr-only">Username</label>
        <input type="username" id="inputUsername" name="username" class="form-control" placeholder="Username" required autofocus>
        <br>
        <label for="inputPassword" class="sr-only">Password</label>
        <input type="password" id="inputPassword" name="password" class="form-control" placeholder="Password" required>
        <div class="checkbox mb-3">
            <label>
                <?= $notif ?>
            </label>
        </div>
        <button class="btn btn-lg btn-danger btn-block" type="submit">OK I'm sign in</button>
        <p class="mt-5 mb-3 text-muted">Your Damn Exercise &copy; 2023</p>
    </form>
</body>

</html>