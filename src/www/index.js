async function GetUserCounts() {
  try {
    return await (await fetch("/counts")).json();
  } catch {
    return {
      "2d": "?",
      "3d": "?",
    };
  }
}

async function UpdateDisplayCounts() {
  const counts = await GetUserCounts();
  document.getElementById("count-2d").innerText = `[${counts["2d"]}]`;
  document.getElementById("count-3d").innerText = `[${counts["3d"]}]`;
}

UpdateDisplayCounts();
setInterval(async () => await UpdateDisplayCounts(), 5000);
