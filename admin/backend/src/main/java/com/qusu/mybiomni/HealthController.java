package com.qusu.mybiomni;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/health")
public class HealthController {

    @RequestMapping("/alive")
    public String alive() {
        return "{\"status\":200}";
    }
}
