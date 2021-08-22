import http from "k6/http";
import { check } from "k6";

export let options = {
  stages: [
    {
      duration: "5s",
      target: 20
    },
    {
      duration: "10s",
      target: 20
    }
  ]
};

export default function() {
  const params = {
    headers: {
      "Content-Type": "application/json"
    }
  };
  const url = __ENV.API_URL || "https://django-graphql-benchmark.herokuapp.com";
  const response = http.get(`${url}/drf-api/movies/`, null, params);

  check(response, {
    "is status 200": r => r.status === 200
  });
  check(response, {
    "is response correct": r => {
      return (
        response.json().length === 250 &&
        response.json()[0].title === "The Shawshank Redemption"
      );
    }
  });
}
