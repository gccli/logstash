input {
  udp {
    port => 5520
    add_field => {
      "vendor" => "waf"
      "category" => "attack"
    }
  }
}

filter {
}


output {
  stdout { codec => rubydebug }
}
