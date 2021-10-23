# nvim-profiler

This is a minimal python script to profile the startup time for (neo)vim. The
script provides configuration options for profiling different commands, enabling
support for either vim or neovim. It also permits the profiling of opening
files, or running vim commands.

The focus of the profiler is to generate easy to interpret and understand output
for the user. To help users to understand what might be slowing down their
vim startup times.

## Formats

The script currently implements three formatting options: `table`, `graph`,
`tree`.

### Table

The table formatting option, is the default option, and can be explicitly set
using `--format table`. The table includes the file names for each file that was
sources, along with data about the time required for loading each file. The
_Perc_ field is the percentage of the total time that was spent sourcing that
file. When multiple samples are available, _Min_, _Average_, _Max_, and _Stdev_,
are the minimum, average, maximum, and standard deviation of the samples
respectively.

```txt
                  Neovim startup times (total: 67.949ms)                   
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┓
┃ File                  ┃ Perc   ┃ Min     ┃ Average ┃ Max     ┃ Stdev    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━┩
│ packer_compiled.lua   │ 39.41% │  26.413 │  26.782 │  27.771 │ 2.88e-01 │
│ init.lua              │ 39.13% │  25.705 │  26.590 │  27.660 │ 4.49e-01 │
│ onedark.vim           │ 27.68% │  18.499 │  18.809 │  19.030 │ 1.24e-01 │
│ filetype.vim          │  5.51% │   3.676 │   3.745 │   3.848 │ 3.98e-02 │
│ syntax.vim            │  5.35% │   3.555 │   3.635 │   3.803 │ 4.50e-02 │
│ synload.vim           │  5.23% │   3.479 │   3.556 │   3.724 │ 4.45e-02 │
│ syncolor.vim          │  3.60% │   2.381 │   2.448 │   2.501 │ 2.64e-02 │
│ galaxyline.lua        │  0.45% │   0.274 │   0.308 │   0.671 │ 5.44e-02 │
│ dashboard.vim         │  0.25% │   0.164 │   0.172 │   0.355 │ 2.66e-02 │
│ gzip.vim              │  0.19% │   0.124 │   0.128 │   0.137 │ 2.46e-03 │
│ zipPlugin.vim         │  0.16% │   0.106 │   0.112 │   0.127 │ 4.37e-03 │
│ matchparen.vim        │  0.14% │   0.089 │   0.094 │   0.103 │ 2.85e-03 │
│ tarPlugin.vim         │  0.13% │   0.086 │   0.090 │   0.095 │ 2.42e-03 │
│ rplugin.vim           │  0.13% │   0.085 │   0.087 │   0.097 │ 2.19e-03 │
│ shada.vim             │  0.09% │   0.060 │   0.063 │   0.069 │ 1.71e-03 │
│ man.vim               │  0.07% │   0.047 │   0.048 │   0.053 │ 8.58e-04 │
│ nvim-web-devicons.vim │  0.05% │   0.034 │   0.036 │   0.043 │ 1.49e-03 │
│ sysinit.vim           │  0.04% │   0.024 │   0.026 │   0.031 │ 1.31e-03 │
│ plenary.vim           │  0.03% │   0.020 │   0.021 │   0.024 │ 6.67e-04 │
│ ftplugin.vim          │  0.03% │   0.020 │   0.020 │   0.021 │ 4.43e-04 │
│ indent.vim            │  0.03% │   0.017 │   0.018 │   0.021 │ 7.94e-04 │
│ spellfile.vim         │  0.02% │   0.014 │   0.015 │   0.021 │ 1.08e-03 │
│ meson.vim             │  0.02% │   0.013 │   0.014 │   0.020 │ 1.11e-03 │
│ nightfox.vim          │  0.02% │   0.012 │   0.013 │   0.023 │ 1.54e-03 │
│ netrwPlugin.vim       │  0.02% │   0.010 │   0.011 │   0.012 │ 6.47e-04 │
│ tutor.vim             │  0.02% │   0.010 │   0.011 │   0.012 │ 5.51e-04 │
│ archlinux.vim         │  0.01% │   0.008 │   0.009 │   0.011 │ 4.95e-04 │
│ which-key.vim         │  0.01% │   0.006 │   0.007 │   0.011 │ 7.35e-04 │
│ matchit.vim           │  0.01% │   0.007 │   0.007 │   0.008 │ 1.98e-04 │
│ tohtml.vim            │  0.01% │   0.007 │   0.007 │   0.008 │ 1.98e-04 │
│ health.vim            │  0.01% │   0.006 │   0.007 │   0.007 │ 3.70e-04 │
│ rplugin.vim           │  0.01% │   0.006 │   0.007 │   0.008 │ 5.42e-04 │
└───────────────────────┴────────┴─────────┴─────────┴─────────┴──────────┘
```

### Graph

The graph formatting option can be enabled using `--format graph`. The graph is
a horizontal bar graph, where each row is a different file being sourced, and
the bar length is representative of the time required for sourcing that file.

```txt
                   Neovim startup times (total: 67.962ms)                   
                                                                            
                   File   Startup Time (Avg)                                
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
               init.lua   ███████████████████████████████████████▏ 23.91ms  
            onedark.vim   ███████████████████████████▏ 16.71ms              
    packer_compiled.lua   ██████████████████████▏ 13.43ms                   
           filetype.vim   ██████▏  3.72ms                                   
           syncolor.vim   ████▏  2.45ms                                     
         galaxyline.lua   ▏  0.30ms                                         
          dashboard.vim   ▏  0.17ms                                         
               gzip.vim   ▏  0.13ms                                         
            synload.vim   ▏  0.13ms                                         
          zipPlugin.vim   ▏  0.11ms                                         
         matchparen.vim   ▏  0.09ms                                         
          tarPlugin.vim   ▏  0.09ms                                         
            rplugin.vim   ▏  0.08ms                                         
             syntax.vim   ▏  0.08ms                                         
              shada.vim   ▏  0.06ms                                         
                man.vim   ▏  0.05ms                                         
  nvim-web-devicons.vim   ▏  0.04ms                                         
            plenary.vim   ▏  0.02ms                                         
           ftplugin.vim   ▏  0.02ms                                         
             indent.vim   ▏  0.02ms                                         
            sysinit.vim   ▏  0.02ms                                         
          spellfile.vim   ▏  0.02ms                                         
              meson.vim   ▏  0.01ms                                         
           nightfox.vim   ▏  0.01ms                                         
              tutor.vim   ▏  0.01ms                                         
        netrwPlugin.vim   ▏  0.01ms                                         
          archlinux.vim   ▏  0.01ms                                         
          which-key.vim   ▏  0.01ms                                         
            matchit.vim   ▏  0.01ms                                         
             tohtml.vim   ▏  0.01ms                                         
             health.vim   ▏  0.01ms                                         
            rplugin.vim   ▏  0.01ms                                         
```

### Tree

The tree formatting option can be enabled using `--format tree`. This formatter
generates a tree of the files that were sourced during vim startup. This can be
useful for visualizing which plugins provide each file that was sourced. The
tree also includes the milliseconds required to source all child nodes in the
tree. It also includes what percentage of the parent node duration was spent
sourcing each child node, and each nodes percentage of the total startup time.
These values are given in the format `<source time> <percentage of parent>
<percentage of total>`.

```
                     Neovim startup times (total: 67.909ms)                     
/ 61.66ms 90.80% (90.80%)                                                                                                                                                                    
├── home/<user>/ 54.53ms 88.43% (80.30%)                                                                                                                                                      
│   ├── .config/nvim/ 37.27ms 68.35% (54.88%)                                                                                                                                                
│   │   ├── init.lua 23.89ms 64.10% (35.18%)                                                                                                                                                 
│   │   └── plugin/packer_compiled.lua 13.38ms 35.90% (19.70%)                                                                                                                               
│   └── .local/share/nvim/ 17.26ms 31.65% (25.41%)                                                                                                                                           
│       ├── site/pack/packer/ 17.25ms 99.96% (25.41%)                                                                                                                                        
│       │   ├── start/ 16.89ms 97.93% (24.88%)                                                                                                                                               
│       │   │   ├── onedark.nvim/colors/onedark.vim 16.71ms 98.89% (24.60%)                                                                                                                  
│       │   │   ├── dashboard-nvim/plugin/dashboard.vim  0.17ms 1.00% (0.25%)                                                                                                                
│       │   │   ├── nightfox.nvim/plugin/nightfox.vim  0.01ms 0.08% (0.02%)                                                                                                                  
│       │   │   └── which-key.nvim/plugin/which-key.vim  0.01ms 0.04% (0.01%)                                                                                                                
│       │   └── opt/  0.36ms 2.07% (0.53%)                                                                                                                                                   
│       │       ├── galaxyline.nvim/plugin/galaxyline.lua  0.30ms 83.94% (0.44%)                                                                                                             
│       │       ├── nvim-web-devicons/plugin/nvim-web-devicons.vim  0.04ms 10.09% (0.05%)                                                                                                    
│       │       └── plenary.nvim/plugin/plenary.vim  0.02ms 5.97% (0.03%)                                                                                                                    
│       └── rplugin.vim  0.01ms 0.04% (0.01%)                                                                                                                                                
├── usr/share/  7.12ms 11.54% (10.48%)                                                                                                                                                       
│   ├── nvim/  7.10ms 99.80% (10.46%)                                                                                                                                                        
│   │   ├── runtime/  7.09ms 99.87% (10.44%)                                                                                                                                                 
│   │   │   ├── filetype.vim  3.73ms 52.57% (5.49%)                                                                                                                                          
│   │   │   ├── syntax/  2.65ms 37.37% (3.90%)                                                                                                                                               
│   │   │   │   ├── syncolor.vim  2.45ms 92.25% (3.60%)                                                                                                                                      
│   │   │   │   ├── synload.vim  0.13ms 4.82% (0.19%)                                                                                                                                        
│   │   │   │   └── syntax.vim  0.08ms 2.93% (0.11%)                                                                                                                                         
│   │   │   ├── plugin/  0.68ms 9.52% (0.99%)                                                                                                                                                
│   │   │   │   ├── gzip.vim  0.13ms 19.12% (0.19%)                                                                                                                                          
│   │   │   │   ├── zipPlugin.vim  0.11ms 16.68% (0.17%)                                                                                                                                     
│   │   │   │   ├── matchparen.vim  0.09ms 14.03% (0.14%)                                                                                                                                    
│   │   │   │   ├── tarPlugin.vim  0.09ms 13.35% (0.13%)                                                                                                                                     
│   │   │   │   ├── rplugin.vim  0.08ms 11.94% (0.12%)                                                                                                                                       
│   │   │   │   ├── shada.vim  0.06ms 9.22% (0.09%)                                                                                                                                          
│   │   │   │   ├── man.vim  0.05ms 7.21% (0.07%)                                                                                                                                            
│   │   │   │   ├── spellfile.vim  0.01ms 2.19% (0.02%)                                                                                                                                      
│   │   │   │   ├── tutor.vim  0.01ms 1.58% (0.02%)                                                                                                                                          
│   │   │   │   ├── netrwPlugin.vim  0.01ms 1.57% (0.02%)                                                                                                                                    
│   │   │   │   ├── matchit.vim  0.01ms 1.04% (0.01%)                                                                                                                                        
│   │   │   │   ├── tohtml.vim  0.01ms 1.04% (0.01%)                                                                                                                                         
│   │   │   │   └── health.vim  0.01ms 1.02% (0.01%)                                                                                                                                         
│   │   │   ├── ftplugin.vim  0.02ms 0.29% (0.03%)                                                                                                                                           
│   │   │   └── indent.vim  0.02ms 0.25% (0.03%)                                                                                                                                             
│   │   └── archlinux.vim  0.01ms 0.13% (0.01%)                                                                                                                                              
│   └── vim/vimfiles/ftdetect/meson.vim  0.01ms 0.20% (0.02%)                                                                                                                                
└── etc/xdg//nvim/sysinit.vim  0.02ms 0.03% (0.03%)                                                                                                                                          
```
