{-# LANGUAGE OverloadedStrings #-}
import Network.HTTP
import Network.HTTP.Conduit
import Text.HTML.DOM
import Text.XML.Cursor
import qualified Data.Text as T
import qualified Data.Text.Lazy as TL
import Data.Text.Lazy.Encoding as E
import Data.Encoding
import Data.Encoding.CP1251
import Data.Encoding.UTF8

openURL x =  do 
  x <- simpleHTTP (getRequest x)
  fmap (decodeString CP1251) (getResponseBody x)

main = do
  let a = "{\n\t\"tags\" : [\n\t\t"
  let url = "http://www.povarenok.ru/recipes/show/137050/"
--  heresy <- simpleHttp url
  heresy <- openURL url
  let cursor = fromDocument $ parseLBS $ encodeUtf8 $ TL.pack heresy
--  print $ T.concat $
--    child cursor >>= element "head" >>= child >>= element "title"
--                 >>= descendant >>= content
--    cursor $// (element "body" >=> child >=> attributeIs "id" "topcontainer" >=> child >=> attributeIs "id" "middle">=> child >=> attributeIs "id" "container">=> child >=> attributeIs "id" "content">=> child >=> attributeIs "id" "print_body" >=> child >=> attributeIs "class" "gray" >=> child >=> element "a") &| (T.concat . content)

--   let ctt = child cursor >>= content
  let ctt = child cursor >>= element "head" >>= child >>= element "title" >>= descendant >>= content
  print $ TL.unpack  $ TL.concat $ map TL.fromStrict ctt

