async function FetchWrapper(
  args = {
    url: "",
    headers: {},
    method: "",
    data: null,
  },
) {
  const res = await fetch(args.url, {
    method: args.method,
    headers: {
      "content-type": "application/json",
      ...args.headers,
    },
    body: args.data ? JSON.stringify(args.data) : null,
  })
    .then((res) => res.text())
    .catch((e) => {
      console.log(e);
      return {
        success: false,
        status_code: 0,
        message: "Network request failed.",
      };
    });
  try {
    const json = JSON.parse(res);
    return json;
  } catch (e) {
    return {
      success: false,
      status_code: 0,
      message: "JSON parse failed.",
    };
  }
}

async function Register(username, password) {
  return await FetchWrapper({
    url: "/api/register",
    method: "POST",
    data: {
      username,
      password,
    },
  });
}

async function Login(username, password) {
  return await FetchWrapper({
    url: "/api/login",
    method: "POST",
    data: {
      username,
      password,
    },
  });
}

async function Logout(user_id) {
  return await FetchWrapper({
    url: "/api/logout",
    method: "POST",
    headers: {
      authorization: `Bearer ${localStorage.getItem("token")}`,
    },
    data: {
      user_id,
    },
  });
}
