使用方法
本站开放API接口分两个，一个是获取当日壁纸，另一个是随机获取Bing历史壁纸（收录范围从2020-09-01至今）。

所有接口都是支持直接使用的链接，可以直接把它当做一个图片url链接来用，插入如下代码：

Bing今日壁纸（长期提供服务，地球不停转，我们不停服）

<img src="https://bing.img.run/uhd.php" alt="Bing每日壁纸UHD超高清原图" />
<img src="https://bing.img.run/1920x1080.php" alt="Bing每日壁纸1080P高清" />
<img src="https://bing.img.run/1366x768.php" alt="Bing每日壁纸普清" />
<img src="https://bing.img.run/m.php" alt="Bing每日壁纸手机版1080P高清" />
随机获取Bing历史壁纸

<img src="https://bing.img.run/rand_uhd.php" alt="随机获取Bing历史壁纸UHD超高清原图" />
<img src="https://bing.img.run/rand.php" alt="随机获取Bing历史壁纸1080P高清" />
<img src="https://bing.img.run/rand_1366x768.php" alt="随机获取Bing历史壁纸普清" />
<img src="https://bing.img.run/rand_m.php" alt="随机获取Bing历史壁纸手机版1080P高清" />
随机获取的Bing历史壁纸库从2020-09-01至今！

代码开源
开源，是一种互联网精神。本站所有壁纸均来自Bing、开放API接口也是基于Bing官方接口进行制作。本着取之于民用之于民的原则，本人将本站开放API接口开源在Github上。链接：

https://github.com/mike126126/bing

将Github代码克隆一份到你自己的主机（服务器）上，绑定好域名，即可访问。

需要注意的是，PHP直接输出图片的方式，图片访问走的是服务器流量，速度受限于服务器速度。建议优先选择“跳转至Bing图片直链”的方式使用，直接输出为Bing图片直链，图片访问不占用服务器流量，速度不受服务器邮箱，更快更好用。

如果您部署源代码部署到自己服务器上，那么就更建议使用302跳转的Bing直链的方式，速度为Bing速度。不想自己部署代码的，可以直接使用bing.img.run提供的API服务。

文件说明
在需要引用图片的地方插入你自己部署好的URL即可。不同参数URL文件说明如下：

uhd.php　PHP链接直接输出4k超高清原图。

uhd_302.php　输出4k超高清原图的Bing直链图片。

1920×1080.php　PHP链接直接输出1920×1080分辨率图片。

1920x1080_302.php　输出为1920×1080分辨率的Bing直链图片。

1366×768.php　PHP链接直接输出1366×768分辨率图片。

1366x768_302.php　输出为1366×768分辨率的Bing直链图片。

m.php　PHP链接直接输出1080×1920分辨率竖版图片。

m_302.php　输出为1080×1920分辨率的Bing直链竖版图片。