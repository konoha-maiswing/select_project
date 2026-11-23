package com.example.demo;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class PageController {

    // タイトル画面
    @GetMapping("/")
    public String title() {
        return "title";
    }

    // メイン画面
    @GetMapping("/main")
    public String main() {
        return "main";
    }

}

