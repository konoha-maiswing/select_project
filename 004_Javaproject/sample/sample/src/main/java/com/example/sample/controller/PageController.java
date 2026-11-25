package com.example.sample.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class PageController {

    // タイトル画面を表示
    @GetMapping("/")
    public String showTitle() {
        return "title";
    }

    // メイン画面を表示
    @GetMapping("/main")
    public String showMain() {
        return "main";
    }
}

