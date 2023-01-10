import http from "k6/http";
import { check } from "k6";

export let options = {
  stages: [
    {
      duration: "5s",
      target: 10
    },
    {
      duration: "10s",
      target: 10
    }
  ]
};

export default function() {
  const params = {
    headers: {
      "Content-Type": "application/json"
    }
  };
  const response = http.get(`${__ENV.API_HOST}/json-api/top-250`, null, params);

  check(response, {
    "is status 200": r => r.status === 200
  });
  check(response, {
    "is response correct": r => {
      return (
        response.json().data.length === 250 &&
        response.json().data[0].title === "The Shawshank Redemption"
      );
    }
  });
}
