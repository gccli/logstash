input {
  udp {
    port => 5510
    add_field => {
      "vendor" => "vfw"
      "category" => "traffic"
    }
  }
  udp {
    port => 5511
    add_field => {
      "vendor" => "vfw"
      "category" => "threat"
    }
  }

  udp {
    port => 5514
    add_field => {
      "vendor" => "vfw"
      "category" => "event"
    }
  }
}

filter {
  if [category] == "event" {
     kv {}

     date {
        match => [ "time", "UNIX" ]
     }
     mutate {
        rename => { "host" => "client_ip" }
     }
  }
}

output {
  stdout { codec => rubydebug }
}
